import logging
import socket
import os
from concurrent.futures import ThreadPoolExecutor

from conf.config import BUFFER_SIZE, SERVER_IP, SERVER_PORT, SERVER_FOLDER, MESSAGE_OK
from src.lib.segment import Segment
from src.lib.stop_and_wait_protocol import StopAndWaitProtocol

logging.basicConfig(level=logging.INFO)


class FileTransferServer:
    def __init__(self, server_ip, server_port, buffer_size, server_folder, max_workers):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.server_folder = server_folder
        self.max_workers = max_workers
        logging.basicConfig(level=logging.INFO)

    def create_file(self, file_name):
        file = open(file_name, "wb")
        return file

    def create_socket(self):
        self.server_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )
        self.server_socket.bind((self.server_ip, self.server_port))
        logging.info("UDP server up and listening")

    def receive_file_name(self):
        file_name, address = self.server_socket.recvfrom(self.buffer_size)
        logging.info(f"File name received: {file_name}")
        self.server_socket.sendto(MESSAGE_OK, address)
        logging.info("The client is notified that the file name has been received")
        return file_name.decode()

    def receive_file_data(self, file):
        logging.info(f"Receiving file data")
        while True:
            data, address = self.server_socket.recvfrom(self.buffer_size)
            if data.decode() == "UPLOAD_END":
                break
            file.write(data)
        logging.info(f"File data received successfully")
        self.server_socket.sendto(MESSAGE_OK, address)
        logging.info("The client is notified that the data has been received")

    def receive_file(self):
        file_name = self.receive_file_name(self)
        file = self.create_file(os.path.join(self.server_folder, file_name))
        self.receive_file_data(file)

    def download_file(self, address, file_name):
        file_path = os.path.join(self.server_folder, file_name)
        protocol = StopAndWaitProtocol(self.server_socket, address)
        try:
            protocol.send_file(file_path)
        except FileNotFoundError as e:
            logging.error(f"File {file_path} not found.")
            self.server_socket.sendto("FILE_NOT_FOUND".encode(), address)
        except ConnectionError as e:
            logging.error(f"Connection lost for address {address}"
        except Exception as e:
            logging.error(f"Error while downloading: {str(e)}")
            self.server_socket.sendto("ERROR_DOWNLOADING_FILE".encode(), address)
    def start(self):
        self.create_socket()
        while True:
            task, address = self.server_socket.recvfrom(self.buffer_size)

            if task.decode() == "UPLOAD_START":
                logging.info(f"Upload start from {address}")
                self.receive_file(self.server_socket)
                logging.info("The file upload has been completed successfully")

            if task.decode().split()[0] == "DOWNLOAD_START":
                logging.info(f"Download start from {address}")
                self.download_file(address, task.decode().split()[1])
                logging.info("The file download has been completed successfully")

            else:
                error_message = "Command not valid."
                self.server_socket.send(error_message.encode())
                self.server_socket.close()


if __name__ == "__main__":
    server = FileTransferServer(SERVER_IP, SERVER_PORT, BUFFER_SIZE, SERVER_FOLDER)
    server.start()
