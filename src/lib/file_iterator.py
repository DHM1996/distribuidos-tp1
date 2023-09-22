import os


class FileIterator:
    def __init__(self, file_path, read_size):
        self.read_size = read_size
        if not os.path.isfile(file_path):
            raise FileNotFoundError
        self.file = open(self.file_path, 'rb')

    def __iter__(self):
        return self

    def __next__(self):
        data = self.file.read(self.read_size)
        if not data:
            self.file.close()
            raise StopIteration
        return data
