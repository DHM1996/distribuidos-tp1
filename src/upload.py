import logging
import os
import socket
import sys

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 8081

BUFFER_SIZE = 1024

CLIENT_FOLDER = os.getcwd() + os.sep + ".." + os.sep + "client_files" + os.sep

logging.basicConfig(level=logging.INFO)


class ServerException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"Server Error: {self.message}"


class ClientException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"Client Error: {self.message}"


def create_socket():
    client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    logging.info("Socket created")
    return client_socket


def close_socket(client_socket):
    client_socket.close()


def open_file(file_name):
    logging.info(f"Trying to open file {file_name}")
    try:
        file = open(CLIENT_FOLDER + file_name, "rb")
        logging.info("File opened successfully")
    except FileNotFoundError:
        raise ClientException(f"File not found")
    return file


def send_upload_start_message(client_socket):
    logging.info("Notifying the server of a new file upload")
    client_socket.sendto(str.encode("UPLOAD_START"), (SERVER_IP, SERVER_PORT))


def send_upload_end_message(client_socket):
    logging.info("Notifying the server that the upload has finished")
    client_socket.sendto(str.encode("UPLOAD_END"), (SERVER_IP, SERVER_PORT))


def wait_server_for_file_name_confirmation(client_socket):
    logging.info("Waiting for file name confirmation")
    response, address = client_socket.recvfrom(BUFFER_SIZE)
    if response.decode() != "Ok":
        raise ServerException(response)
    logging.info("File name confirmation received successfully")


def wait_server_for_file_data_confirmation(client_socket):
    logging.info("Waiting for file data confirmation")
    response, address = client_socket.recvfrom(BUFFER_SIZE)
    if response.decode() != "Ok":
        raise ServerException(response)
    logging.info("File data confirmation received successfully")


def send_file_name(file_name, client_socket):
    logging.info("Sending file name to the server")
    file_name = str.encode(file_name)
    client_socket.sendto(file_name, (SERVER_IP, SERVER_PORT))
    logging.info("File name has been sent successfully")


def send_file_data(file, client_socket):
    logging.info("Sending file data to the server")
    while True:
        data = file.read(BUFFER_SIZE)
        if not data:
            return
        client_socket.sendto(data, (SERVER_IP, SERVER_PORT))


def upload_file(file_name: str):
    file = open_file(file_name)
    client_socket = create_socket()
    send_upload_start_message(client_socket)
    send_file_name(file_name, client_socket)
    wait_server_for_file_name_confirmation(client_socket)
    send_file_data(file, client_socket)
    send_upload_end_message(client_socket)
    wait_server_for_file_data_confirmation(client_socket)
    close_socket(client_socket)


def execute():
    argv = sys.argv
    file_name = argv[1]
    try:
        upload_file(file_name)
    except (ClientException or ServerException) as err:
        logging.error(err)


if __name__ == '__main__':
    execute()
