import os


class FileIterator:
    def __init__(self, file_path, read_size):
        self.read_size = read_size
        if not os.path.isfile(file_path):
            raise FileNotFoundError
        self.file = open(file_path, 'rb')
        self.file_path = file_path
        self.file_data = []

        with open(self.file_path, 'rb') as file:
            while True:
                data = file.read(self.read_size)
                if not data:
                    break
                self.file_data.append(data)

    def __iter__(self):
        return self

    def __next__(self):
        data = self.file.read(self.read_size)
        if not data:
            self.file.close()
            raise StopIteration
        self.file_data.append(data)
        return data

    def get_part(self, i):
        if i < 0 or i >= len(self.file_data):
            raise IndexError("Index out of range.")
        return self.file_data[i]

    def get_length(self):
        return len(self.file_data)
