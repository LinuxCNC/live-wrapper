
import os
import tempfile

class CDRoot:
    def __init__(self, path=None):
        if not path:
            self.path = tempfile.mkdtemp()
        else:
            self.path = path
            if not os.path.exists(path):
                os.makedirs(path)

    def __getitem__(self, i):
        return CDRoot(os.path.join(self.path, i))
        
    def __str__(self):
        return self.path
