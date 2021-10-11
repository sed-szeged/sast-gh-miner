import shutil
import os


class FileMover:
    def __init__(self, files, destination):
        self.files = [os.path.abspath(file) for file in files]
        self.destination = os.path.abspath(destination)

    def move_files(self):
        for file in self.files:
            shutil.move(file, self.destination)
