# linux-cheatsheet
List of useful commands and configs for setting up a Linux system

## Mounting a Samba share
Mounting a share requires root. To allow the share to be owned by another user, specify the UID and GID options. UIDs and GIDs can be found using the `id` command.

The username and password here are the credentials for the Samba share.

If you don't want password written out in plaintext, omitting the password option will prompt you after running the command. 

Syntax:
`sudo mount -t cifs -o username=<username>,password=<password>,uid=<desired UID>,gid=<desired GID>,vers=2.0 //<IP or hostname>/<shared folder> <desired mount point on local system>`

The version parameter is important to specify or it will default to 1.0 and the operation will fail.

Example:
`sudo mount -t cifs -o username=admin,password=123,uid=1001,gid=1001,vers=2.0 //nas/share /media/nas`

### Unmounting a Samba share (or any mounted filesystem)
`sudo umount <path to share>`

## Linux software RAID Array

### Formatting Disks for use with Linux RAID

Use `parted` to change the partition type to GPT (for disks over 2 TB)

Use `fdisk` to create a partition of type `Linux RAID auto` for the full size of the drive

See [this guide](https://www.tecmint.com/create-raid-6-in-linux/) for details.

### Setting up the array

Follow [this guide](https://www.digitalocean.com/community/tutorials/how-to-create-raid-arrays-with-mdadm-on-ubuntu-18-04)

To mount the array on boot, put configs in `/etc/mdadm.conf` instead of `/etc/mdadm/mdadm.conf` as the tutorial suggests.

### Growing an existing array

Pretty simple, use `mdadm --add` to add the new device to the array, and then use `mdadm --grow` to grow the array.

Growing will trigger an array reshape, which can take days to complete for large arrays.

Details in [this guide](https://raid.wiki.kernel.org/index.php/Growing)

Once the reshape has been completed, the filesystem needs to be resized to match the new size.
This can be done using: `resize2fs -p /dev/md0`

Finally, the `mdadm.conf` needs to updated to reflect the new devices.

### Reassembling an existing array

When moving to a new system or install, use the previous `mdadm.conf` to reassemble the array: `mdadm --assemble --conf mdadm.conf`

Then follow the same instructions as creation to mount the filesystem.

### Stopping a RAID resync

RAID arrays will automatically perform checks every once in a while. This may cause degraded performance while the check is happening. To stop the checks after they have been started, you can use the `checkarray` script in Debian/Ubuntu distributions. It can be found at `/usr/share/mdadm/checkarray`.

Use `checkarray -x --all` to stop in-progress checks.

## Terminal Colors over SSH
Often the terminal over SSH is all the same color, which can be a little difficult to use. This can be fixed by uncommenting or adding the following line in the remote `.bashrc`:

`force_color_prompt=yes`

Then in the remote server's `.bash_profile`, add the following to load your `.bashrc` on login:
```
  if [ -f ~/.bashrc ]; then
    . ~/.bashrc
  fi
```

## SSH Tunneling

To access web apps being served on localhost on a remote server, you can set up an SSH tunnel to access them on your remote machine.

`ssh <username>@<server IP> -L <local port>:localhost:<server port>`.

So for example, if a web app is being served on `localhost:32400` on your server with IP `12.34.56.78` and you want to be able to access it locally on port `8888`, you could run the following on your local machine:

`ssh user@12.34.56.78 -L 8888:localhost:32400`

This is not a permanent solution, as it is only active while your SSH session is active. To do this permanently, you'll want to setup a reverse proxy.



