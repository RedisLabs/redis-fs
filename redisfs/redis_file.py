import os

class RFile(object):
    """Represents a file stored within redis."""

    def __init__(self, path, conn):
        """Creates a new file."""
        super(RFile, self).__init__()
        self.path = path
        self.conn = conn

    @staticmethod
    def Create(path, conn):
        conn.set(path, "")
        return RFile(path, conn)

    def Parent(self):
        dir = os.path.dirname(self.path)

        # Make sure folder exists.
        t = self.conn.type(dir)
        if t == "set":
            from .redis_folder import RFolder
            return RFolder(dir, self.conn)
        else:
            return None

    def Read(self, offset, size):
        """Read `length` bytes at `offset` from file"""
        return self.conn.getrange(self.path, offset, size)

    def Write(self, buff):
        """Writes buff to file"""
        self.conn.set(self.path, buff)
        return self.conn.strlen(self.path)

    def Delete(self):
        """Deletes file and all of its content."""
        parent = self.Parent()
        if parent:
            self.conn.srem(parent.FullPath(), self.Name())

        self.conn.delete(self.path)

    def Name(self):
        """Returns file name"""
        return os.path.basename(self.path)

    def FullPath(self):
        """Returns file full path."""
        return self.path
