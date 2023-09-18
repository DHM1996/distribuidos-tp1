import logging
import socket
import os

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

BUFFER_SIZE = 1024

SERVER_FOLDER = os.getcwd() + os.sep + ".." + os.sep + "server_files" + os.sep

OK = str.encode("Ok")

logging.basicConfig(level=logging.INFO)


def create_file(file_name):
    file = open(file_name, 'wb')
    return file


def create_socket():
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    logging.info("UDP server up and listening")
    return server_socket


def receive_file_name(server_socket):
    file_name, address = server_socket.recvfrom(BUFFER_SIZE)
    logging.info(f"File name received: {file_name}")
    server_socket.sendto(OK, address)
    logging.info("The client is notified that the file name has been received")
    return file_name.decode()


def receive_file_data(file, server_socket):
    logging.info(f"Receiving file data")
    while True:
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        if data.decode() == "UPLOAD_END":
            break
        file.write(data)
    logging.info(f"File data received successfully")
    server_socket.sendto(OK, address)
    logging.info("The client is notified that the data has been received")


def receive_file(server_socket):
    file_name = receive_file_name(server_socket)
    file = create_file(SERVER_FOLDER + file_name)
    receive_file_data(file, server_socket)


def execute():
    server_socket = create_socket()
    while True:
        task, address = server_socket.recvfrom(BUFFER_SIZE)

        if task.decode() == "UPLOAD_START":
            logging.info(f"Upload start from {address}")
            receive_file(server_socket)
            logging.info("The file upload has been completed successfully")


if __name__ == '__main__':
    execute()
