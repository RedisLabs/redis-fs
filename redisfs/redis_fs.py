import os
from .redis_file import RFile
from .redis_folder import RFolder

class RFS(object):
    def __init__(self, conn):
        super(RFS, self).__init__()
        self.conn = conn

    def CreateFile(self, path):
        dir_name = os.path.dirname(path)
        file_name = os.path.basename(path)

        # Make sure folder exists.
        folder = self.GetFolder(dir_name)
        if folder is None:
            # TODO throw exception.
            return None

        # Make sure file doesn't exits.
        file = self.GetFile(path)
        if file is not None:
            # TODO throw exception.
            return None

        file = RFile.Create(path, self.conn)

        # Add file to folder.
        folder.AddItem(file)

        return file

    def CreateFolder(self, path):
        # Make sure folder doesn't already exists.
        folder = self.GetFolder(path)
        if folder is not None:
            # TODO throw exception.
            return None

        folder = RFolder.Create(path, self.conn)

        # Add folder as a member of it's parent.
        parent = os.path.dirname(path)
        if parent != path: # Don't look for root's parent.
            parent = self.GetFolder(parent)
            parent.AddItem(folder)

        return folder

    def GetFolder(self, path):
        # Make sure folder exists.
        t = self.conn.type(path).decode("utf-8")
        if t == "set":
            return RFolder(path, self.conn)
        else:
            return None

    def GetFile(self, path):
        # Make sure file exists.
        t = self.conn.type(path).decode("utf-8")
        if t == "string":
            return RFile(path, self.conn)
        else:
            return None

    def GetItem(self, path):
        # Look up path and its type.
        t = self.conn.type(path).decode("utf-8")
        if t == "set":
            return RFolder(path, self.conn)
        elif t == "string":
            return RFile(path, self.conn)
        else:
            return None
