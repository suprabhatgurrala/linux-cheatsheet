# Useful commands for manipulating Video/Audio files using FFMPEG, MKVMerge, etc.
## [Removing EIA-608 closed captions](https://stackoverflow.com/questions/48177694/removing-eia-608-closed-captions-from-h-264-without-reencode)
`ffmpeg -i input.mkv -codec copy -bsf:v "filter_units=remove_types=6" output.mkv`
