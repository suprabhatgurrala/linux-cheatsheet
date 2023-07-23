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
This can be done using: `resize2fs -p /dev/md0`. Note that it might be faster and/or safer to unmount the filesystem before resizing it.

Finally, the `mdadm.conf` needs to updated to reflect the new devices.

### Reassembling an existing array

When moving to a new system or install, use the previous `mdadm.conf` to reassemble the array: `mdadm --assemble --conf mdadm.conf`

Then follow the same instructions as creation to mount the filesystem.

### Stopping a RAID resync

RAID arrays will automatically perform checks every once in a while. This may cause degraded performance while the check is happening. To stop the checks after they have been started, you can use the `checkarray` script in Debian/Ubuntu distributions. It can be found at `/usr/share/mdadm/checkarray`.

Use `checkarray -x --all` to stop in-progress checks.

## MergerFS + SnapRAID

Another option for software RAID which is more flexible with different size drives, with some tradeoffs for performance and resiliency.

See the following guides:

- [Adding a new disk](https://linuxconfig.org/how-to-add-new-disk-to-existing-linux-system)
- [Change the number of reserved blocks](https://ma.ttias.be/change-reserved-blocks-ext3-ext4-filesystem-linux/)
    - By default `ext4` filesystems reserve 5% of their space for root users. In a large drive this may be significant amount of space, and not necessary if the drive will be part of a mergerFS pool.
- [Setting up MergerFS and SnapRAID](https://selfhostedhome.com/combining-different-sized-drives-with-mergerfs-and-snapraid/)

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

## Polkit Configuration

If you mainly access your Ubuntu machine remotely, you might get many popups asking you to authenticate.
This is because as a remote login, you have fewer privelages than a local login.

You can add custom rules to Polkit to allow your remote user to perform functions that would typically require an admin password.

To allow color profiles and managed devices:

`/etc/polkit-1/localauthority.conf.d/02-allow-colord.conf`
```javascript
polkit.addRule(function(action, subject) {
 if ((action.id == "org.freedesktop.color-manager.create-device" ||
 action.id == "org.freedesktop.color-manager.create-profile" ||
 action.id == "org.freedesktop.color-manager.delete-device" ||
 action.id == "org.freedesktop.color-manager.delete-profile" ||
 action.id == "org.freedesktop.color-manager.modify-device" ||
 action.id == "org.freedesktop.color-manager.modify-profile") &&
 subject.isInGroup("{users}")) {
 return polkit.Result.YES;
 }
});
```

To allow USB mounting:

`/etc/polkit-1/localauthority.conf.d/10-udisks2.conf`
```javascript
// See the polkit(8) man page for more information
// about configuring polkit.

// Allow udisks2 to mount devices without authentication
// for users in the "wheel" group.
polkit.addRule(function(action, subject) {
    if ((action.id == "org.freedesktop.udisks2.filesystem-mount-system" ||
         action.id == "org.freedesktop.udisks2.filesystem-mount") &&
        subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
```

## Holding Packages from Updating

See this [StackOverflow link](https://askubuntu.com/questions/18654/how-to-prevent-updating-of-a-specific-package).

### `dpkg`

Put a package on hold:

```bash
echo "<package-name> hold" | sudo dpkg --set-selections
```

Remove the hold:

```bash
echo "<package-name> install" | sudo dpkg --set-selections
```

Display the status of all your packages:

```bash
dpkg --get-selections
```

Display the status of a single package:

```bash
dpkg --get-selections <package-name>
```

Show all packages on hold:

```
dpkg --get-selections | grep "\<hold$"
```

### `apt`

Hold a package:

```bash
sudo apt-mark hold <package-name>
```

Remove the hold:

```bash
sudo apt-mark unhold <package-name>
```

Show all packages on hold:

```bash
sudo apt-mark showhold
```
