import os
from .redis_file import RFile

class RFolder(object):
    """Represents a folder stored within redis."""

    def __init__(self, path, conn):
        """Creates a new folder."""
        super(RFolder, self).__init__()
        self.path = path
        self.conn = conn

    @staticmethod
    def Create(path, conn):
        conn.sadd(path, ".", "..")
        return RFolder(path, conn)

    def Parent(self):
        dir = os.path.dirname(self.path)

        # Make sure folder exists.
        t = self.conn.type(dir).decode("utf-8")
        if t == "set":
            return RFolder(dir, self.conn)
        else:
            return None

    def List(self):
        """List folder content."""
        content = []
        members = self.conn.smembers(self.path)
        for member in members:
            member = member.decode("utf-8")
            member_full_path = os.path.join(self.path, member)
            t = self.conn.type(member_full_path).decode("utf-8")
            if t == "string":
                content.append(RFile(member_full_path, self.conn))
            elif t == "set":
                content.append(RFolder(member_full_path, self.conn))
            else:
                if member == "." or member == "..":
                    content.append(RFolder(member_full_path, self.conn))
                else:
                    # TODO: throw exception
                    continue

        # Sort content.
        content.sort(key=lambda x: x.Name(), reverse=True)
        return content

    def AddItem(self, item):
        """Adds an item (file/folder)."""
        if type(item) is RFile:
            file = item
            self.conn.sadd(self.path, file.Name())
        elif type(item) is RFolder:
            folder = item
            self.conn.sadd(self.path, folder.Name())
        else:
            # TODO: throw exception.
            return None

    def RemoveItem(self, item):
        """Removes an item (file/folder)."""
        self.conn.srem(self.path, item)

    def Delete(self):
        """Deletes folder and all of its content recursively."""
        for item in self.List():
            # Wasteful!
            item.Delete()

        self.conn.delete(self.path)

    def Name(self):
        """Returns folder name"""
        return os.path.basename(self.path)

    def FullPath(self):
        """Returns folder full path."""
        return self.path
