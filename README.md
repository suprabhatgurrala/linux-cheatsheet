# linux-cheatsheet
List of useful commands and configs for setting up a Linux system

## Mounting a Samba share
Mounting a share requires root. To allow the share to be owned by another user, specify the UID and GID options. UIDs and GIDs can be found using the `id` command.

The username and password here are the credentials for the Samba share.

If you don't want password written out in plaintext, omitting the password option will prompt you after running the command. 

Syntax:
`sudo mount -t cifs -o username=<username>,password=<password>,uid=<desired UID>,gid=<desired GID>,vers=2.0 //<IP or hostname>/<shared folder> <desired mount point on local system>`

Example:
`sudo mount -t cifs -o username=admin,password=123,uid=1001,gid=1001 //nas/share /media/nas`

### Unmounting a Samba share (or any mounted filesystem)
`sudo umount <path to share>`
