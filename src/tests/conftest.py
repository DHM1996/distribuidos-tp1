import pytest
from random import choice
from string import ascii_letters as alphabet
import sys
import hashlib

from src.lib.file_iterator import FileIterator
from src.lib.lossy_connection import LossyConnection


@pytest.fixture()
def sender_connection():
    sender_connection = LossyConnection("localhost", 12345, timeout=1, loss_rate=0.0, bind_ip="localhost", bind_port=54321)
    yield sender_connection
    sender_connection.close()

@pytest.fixture()
def receiver_connection():
    receiver_connection = LossyConnection("localhost", 54321, timeout=1, loss_rate=0.0, bind_ip="localhost", bind_port=12345)
    yield receiver_connection
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


@pytest.fixture
def helpers():
    return Helpers