# Hardware-Accelerated Tonemapping and Encoding
## 10-bit HEVC 4K HDR to 8-bit AVC 1080p SDR

```ffmpeg -init_hw_device opencl=gpu:0.0 -filter_hw_device gpu -hwaccel cuda -i [INPUT FILE] -vf "hwupload_cuda,scale_cuda=1920:1080,hwdownload,format=p010,hwupload,tonemap_opencl=t=bt709:p=bt709:m=bt709:tonemap=mobius:format=nv12,hwdownload,format=nv12" -codec:v h264_nvenc -preset 18 -profile high -level 41 -rc 1 -cq 18 -rc-lookahead 4 -codec:a copy -codec:s copy -max_muxing_queue_size 9999 [OUTPUT FILE]```

### Explanation of commands:
- `-init_hw_device opencl=gpu:0.0 -filter_hw_device gpu` - sets the hardware filter device to be the GPU, allows for HW-accelerated OpenCL filters
- `-hwaccel cuda` - use CUDA to accelerate video decoding
- `-vf` - video filters
	- `hwupload_cuda` - upload data to GPU memory for use with CUDA filters
	- `scale_cuda` - scale the video, accelerated with CUDA
	- `hwdownload` - download data from GPU memory (VRAM) back to CPU memory (system RAM)
	- `format=p010` - set the pixel format, `p010` refers to 10-bit
	- `hwupload` - upload the data to GPU memory, this time for use with OpenCL
	- `tonemap_opencl` - OpenCL filter to tonemap HDR into SDR, [documentation here](http://underpop.online.fr/f/ffmpeg/help/tonemap_005fopencl.htm.gz)
		- `t=bt709` - colorspace of transfer, `bt709` is the SDR colorspace
			- `p` and `m` are also setting colors to `bt709` SDR
		- `tonemap=mobius` - tonemapping algorithm to use.
			- `mobius` claims to retain color accuracy while sacrificing highlight detail
			- [see here](http://underpop.online.fr/f/ffmpeg/help/tonemap.htm.gz) for documentation of other tonemapping algorithms
		- `format=nv12` - set the output pixel format of the tonemapping filter, `nv12` refers to 8-bit
	- `hwdownload` - download data from GPU memory (VRAM) back to CPU memory (system RAM)
	- `format=nv12` - set the output pixel format, `nv12` refers to 8-bit
- `codec:v h264_nvenc` - use NVIDIA's H264 hardware encoder to encode the video stream. Use `ffmpeg -h encoder=h264_nvenc` to see full documentation of options
	- `-preset 18` - slowest (best quality) encoding preset
	- `-profile high -level 41` - sets the format profile to `High@4.1`, [see here](https://en.wikipedia.org/wiki/Advanced_Video_Coding#Profiles) for more information about profiles in H264/AVC
	- `-rc 1` - set the rate control to variable bitrate mode
	- `cq 18` - set the target quality level for constant quality encoding (similar to `crf` in `x264`)
	- `rc-lookahead 4` - number of frames to lookahead for rate-control
- `codec:a copy` - copy all audio tracks untouched
- `coded:s copy` - copy all subtitle tracks untouched
- `max_muxing_queue_size 9999` - the number of frames that can be queued at once

### Possible Improvements
- Figure out a way to scale using OpenCL or other method that doesn't require uploading and downloading to VRAM twice
- Check for and remove settings that are at default values
- Compare/contrast various parameters with regards to file size, video quality, and encoding time
- Compare/contrast using hardware acceleration vs software based encoding and tonemapping with regards to file size, video quality, and encoding time
