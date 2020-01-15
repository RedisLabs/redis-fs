# redis-fs
Distributed in memory filesystem

## What is this?
RedisFS is a distributed user-space filesystem stored in Redis
This allows for your content to be sorted remotely, auto backed up and shared among others (if you wish) while giving the illusion and the convenience of working locally.

## Prerequisite
* [Fuse](https://github.com/libfuse/libfuse)
* [Python-Fuse](https://github.com/libfuse/python-fuse)

## Usage
Mount: `sudo python main.py <path_to_mount_point>`

Example: `sudo python main.py ~/RedisFS`

You should be able to `cd ~/RedisFS`

All of the content you'll place within `~/RedisFS` will be stored in Redis.

## Unmount
List mounted file systems:  `mount` (output will differ)
```
/dev/disk1s5 on / (apfs, local, read-only, journaled)
devfs on /dev (devfs, local, nobrowse)
/dev/disk1s1 on /System/Volumes/Data (apfs, local, journaled, nobrowse)
/dev/disk1s4 on /private/var/vm (apfs, local, journaled, nobrowse)
map auto_home on /System/Volumes/Data/home (autofs, automounted, nobrowse)
/dev/disk2s1 on /Volumes/GuestCrestronAirMedia (hfs, local, nodev, nosuid, read-only, noowners, quarantine, mounted by roilipman)
/Users/roilipman/Downloads/Atom.app on /private/var/folders/2l/w9kcztpx23588p4m8k3gb5q40000gn/T/AppTranslocation/A6B0503C-616D-488D-A9C1-B502C9067D5C (nullfs, local, nodev, nosuid, read-only, nobrowse, mounted by roilipman)
Python@osxfuse0 on /Users/roilipman/Dev/test_fs (osxfuse, synchronous)
```

Look for `fuse`  and unmount `sudo umount Python@osxfuse0`
