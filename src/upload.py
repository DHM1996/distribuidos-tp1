import logging
import socket
import sys

from src.exceptions.client_exception import ClientException
from src.exceptions.server_exception import ServerException
from conf.config import (
    CLIENT_FOLDER,
    BUFFER_SIZE,
    SERVER_IP,
    SERVER_PORT,
    CLIENT_IP,
    CLIENT_PORT,
)

logging.basicConfig(level=logging.INFO)


class FileUploaderClient:
    def __init__(
        self, server_ip, server_port, client_ip, client_port, buffer_size, client_folder
    ):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_ip = client_ip
        self.client_port = client_port
        self.buffer_size = buffer_size
        self.client_folder = client_folder

    def create_socket(self):
        self.client_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )
        logging.info("Socket created")

    def close_socket(self):
        self.client_socket.close()

    def open_file(self, file_name):
        logging.info(f"Trying to open file {file_name}")
        try:
            file = open(self.client_folder + file_name, "rb")
            logging.info("File opened successfully")
        except FileNotFoundError:
            raise ClientException("File not found")
        return file

    def send_upload_start_message(self):
        logging.info("Notifying the server of a new file upload")
        self.client_socket.sendto(
            str.encode("UPLOAD_START"), (self.server_ip, self.server_port)
        )

    def send_upload_end_message(self):
        logging.info("Notifying the server that the upload has finished")
        self.client_socket.sendto(
            str.encode("UPLOAD_END"), (self.server_ip, self.server_port)
        )

    def wait_server_for_file_name_confirmation(self):
        logging.info("Waiting for file name confirmation")
        response, _ = self.client_socket.recvfrom(self.buffer_size)
        if response.decode() != "Ok":
            raise ServerException(response)
        logging.info("File name confirmation received successfully")

    def wait_server_for_file_data_confirmation(self):
        logging.info("Waiting for file data confirmation")
        response, _ = self.client_socket.recvfrom(self.buffer_size)
        if response.decode() != "Ok":
            raise ServerException(response)
        logging.info("File data confirmation received successfully")

    def send_file_name(self, file_name):
        logging.info("Sending file name to the server")
        file_name = str.encode(file_name)
        self.client_socket.sendto(file_name, (self.server_ip, self.server_port))
        logging.info("File name has been sent successfully")

    def send_file_data(self, file):
        logging.info("Sending file data to the server")
        while True:
            data = file.read(self.buffer_size)
            if not data:
                return
            self.client_socket.sendto(data, (self.server_ip, self.server_port))

    def upload_file(self, file_name):
        file = self.open_file(file_name)
        self.create_socket()
        self.send_upload_start_message()
        self.send_file_name(file_name)
        self.wait_server_for_file_name_confirmation()
        self.send_file_data(file)
        self.send_upload_end_message()
        self.wait_server_for_file_data_confirmation()
        self.close_socket()


if __name__ == "__main__":
    argv = sys.argv
    file_name = argv[1]
    try:
        client = FileUploaderClient(
            SERVER_IP, SERVER_PORT, CLIENT_IP, CLIENT_PORT, BUFFER_SIZE, CLIENT_FOLDER
        )
        client.upload_file(file_name)
    except ClientException or ServerException as err:
        logging.error(err)
