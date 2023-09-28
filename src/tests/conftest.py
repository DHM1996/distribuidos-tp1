import pytest
from random import choice, randint
from string import ascii_letters as alphabet
import sys
import hashlib

from src.lib.file_iterator import FileIterator
from src.lib.lossy_connection import LossyConnection


@pytest.fixture(scope="session")
def connections():
    sender_port = randint(1024, 65535)
    receiver_port = randint(1024, 65535)
    sender_connection = LossyConnection("localhost", receiver_port, timeout=5, loss_rate=0.0, bind_ip="localhost",
                                        bind_port=sender_port)
    receiver_connection = LossyConnection("localhost", sender_port, timeout=5, loss_rate=0.0, bind_ip="localhost",
                                          bind_port=receiver_port)
    yield {"sender_connection": sender_connection, "receiver_connection": receiver_connection}
    sender_connection.close()
    receiver_connection.close()


@pytest.fixture()
def random_5mb_file(tmp_path):
    five_mb = 5 * 1024 * 1024
    file_path = tmp_path / "random_5mb_file.txt"
    with open(file_path, 'w') as f:  # This creates a new file
        for i in range(0, five_mb):
            f.write(choice(alphabet))

    return file_path

class Helpers:
    @staticmethod
    def hash_file(file_path):
        BUF_SIZE = 64 * 1024

        md5 = hashlib.md5()

        file_iterator = FileIterator(file_path, BUF_SIZE)

        for chunk in file_iterator:
            md5.update(chunk)

        return md5.hexdigest()

    @staticmethod
    def string_to_file(string, file_path):
        with open(file_path, 'w') as f:
            f.write(string)

    @staticmethod
    def file_to_string(file_path):
        with open(file_path, 'r') as f:
            return f.read()

@pytest.fixture(scope="session")
def helpers():
    return Helpers