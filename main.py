import os, stat, errno
import fuse
from fuse import Fuse
import redis
import logging
from redisfs import RFS, RFolder, RFile

if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)
log = logging.getLogger(__name__)

redis_con = redis.Redis(host='localhost', port=6379)
redis_con.flushall()

# Create root.
fs = RFS(redis_con)
root = fs.CreateFolder("/")

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0        # protection
        self.st_ino = 0         # inode number
        self.st_dev = 0         # ID of device containing file
        self.st_nlink = 0       # number of hard links
        self.st_uid = 0         # user ID of owner
        self.st_gid = 0         # group ID of owner
        self.st_rdev = 0        # device ID (if special file)
        self.st_size = 0        # total size, in bytes
        self.st_blksize = 0     # blocksize for file system I/O
        self.st_blocks = 0      # number of 512B blocks allocated
        self.st_atime = 0       # time of last access
        self.st_mtime = 0       # time of last modification
        self.st_ctime = 0       # time of last status change

# The following POSIX macros are defined to check the file type using the st_mode field:
# S_ISREG(m) is it a regular file?
# S_ISDIR(m) directory?
# S_ISCHR(m) character device?
# S_ISBLK(m) block device?
# S_ISFIFO(m) FIFO (named pipe)?
# S_ISLNK(m) symbolic link? (Not in POSIX.1-1996.)
# S_ISSOCK(m) socket? (Not in POSIX.1-1996.)

class RedisFS(Fuse):
    #  _attrs = ['getattr', 'readlink', 'readdir', 'mknod', 'mkdir',
    #           'unlink', 'rmdir', 'symlink', 'rename', 'link', 'chmod',
    #           'chown', 'truncate', 'utime', 'open', 'read', 'write', 'release',
    #           'statfs', 'fsync', 'create', 'opendir', 'releasedir', 'fsyncdir',
    #           'flush', 'fgetattr', 'ftruncate', 'getxattr', 'listxattr',
    #           'setxattr', 'removexattr', 'access', 'lock', 'utimens', 'bmap',
    #           'fsinit', 'fsdestroy', 'ioctl', 'poll']

    def getattr(self, path):
        log.debug("getattr, path: {}".format(path))
        st = MyStat()

        item = fs.GetItem(path)
        if type(item) is RFolder:
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
            return st
        elif type(item) is RFile:
            st.st_mode = stat.S_IFREG | 0o664
            st.st_nlink = 1
            st.st_size = redis_con.strlen(path)
            return st

        return -errno.ENOENT

    def readdir(self, path, offset):
        log.debug("readdir, path: %s" % path)
        dir = fs.GetFolder(path)
        if dir is not None:
            for item in dir.List():
                log.debug("readdir, r: %s" % item.Name())
                yield fuse.Direntry(item.Name())

        # for r in redis_con.smembers(path):
        #     log.debug("readdir, r: %s" % r)
        #     yield fuse.Direntry(r)

    def create(self, path, flags, mode):
        logging.debug("create, path: {}, flags: {}, mode: {}".format(path, flags, mode))
        fs.CreateFile(path)
        return None

    def open(self, path, flags):
        log.debug("open, path:{}, flags:{}".format(path, flags))
        item = fs.GetItem(path)
        if item is None:
            return -errno.ENOENT
            # accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
            # if (flags & accmode) != os.O_RDONLY:
            #     return -errno.EACCES
        return None

    def read(self, path, size, offset):
        log.debug("read, path: {}, size: {}, offset: {},".format(path, size, offset))

        file = fs.GetFile(path)
        if file is None:
            return -errno.ENOENT

        return file.Read(offset, size)

    def unlink(self, path):
        log.debug("unlink, path: {}".format(path))
        file = fs.GetFile(path)

        if file is not None:
            file.Delete()
        else:
            return -errno.ENOENT

    def rename(self, oldpath, newpath):
        log.debug("rename")
        # TODO: implement.

    def truncate(self, path, size):
        log.debug("truncate")
        # TODO: implement.

    def write(self, path, buf, offset):
        logging.debug("write, path: {}, buf: {}, offset: {}".format(path, buf, offset))
        file = fs.GetFile(path)
        if file is None:
            logging.debug("File does not exists!")
            return None

        file.Write(buf)
        return len(buf)

        # array = self.buffers.get(path, bytearray())
        # if offset != len(array):
        #     return -errno.EINVAL
        # array[offset:offset+len(buf)] = buf
        # return len(buf)

    def release(self, path, flags):
        log.debug("release")
        # TODO: implement.

    def mkdir(self, path, mode):
        log.debug("mkdir, path: {}, mode: {}".format(path, mode))
        directory = fs.CreateFolder(path)

    def rmdir(self, path):
        log.debug("rmdir, path: {}".format(path))
        dir = fs.GetFolder(path)
        if dir is not None:
            dir.Delete()
        else:
            return -errno.ENOENT

    def chmod(self, path, mode):
        log.debug("chmod, path: {}, mode: {}".format(path, mode))
        # TODO: implement.

def main():
    log.debug("Starting RedisFS")
    logging.basicConfig(filename="log", filemode="w")
    logging.getLogger().setLevel(logging.DEBUG)

    usage="""RedisFS""" + Fuse.fusage

    server = RedisFS(version="%prog " + fuse.__version__, usage=usage, dash_s_do='setsingle')
    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
