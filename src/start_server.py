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


def download_file(server_socket, address, file_name):
    try:
        file_path = SERVER_FOLDER + file_name
        if os.path.exists(file_path):
            logging.info(f"Downloading {file_path} file.")
            with open(file_path, 'rb') as file:
                file_data = file.read()
            server_socket.sendto(file_data, address)
            server_socket.sendto(str.encode("UPLOAD_END"), address)
        else:
            logging.error(f"File {file_path} not found.")
            server_socket.sendto("FILE_NOT_FOUND".encode(), address)
    except Exception as e:
        logging.error(f"Error while downloading: {str(e)}")
        server_socket.sendto("ERROR_DOWNLOADING_FILE".encode(), address)


def execute():
    server_socket = create_socket()
    while True:
        task, address = server_socket.recvfrom(BUFFER_SIZE)

        if task.decode() == "UPLOAD_START":
            logging.info(f"Upload start from {address}")
            receive_file(server_socket)
            logging.info("The file upload has been completed successfully")

        if task.decode().split()[0] == "DOWNLOAD_START":
            logging.info(f"Download start from {address}")
            download_file(server_socket, address, task.decode().split()[1])
            logging.info("The file download has been completed successfully")

        else:
            error_message = "Command not valid."
            server_socket.send(error_message.encode())
            server_socket.close()



if __name__ == '__main__':
    execute()
