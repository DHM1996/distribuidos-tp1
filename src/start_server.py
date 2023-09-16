import logging
import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
BUFFER_SIZE = 1024

logging.basicConfig(level=logging.INFO)


def run():
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    logging.info("UDP server up and listening")

    while True:
        message, address = server_socket.recvfrom(BUFFER_SIZE)

        print("Message from Client:{}".format(message))
        print("Client IP Address:{}".format(address))

        response = str.encode("Received")

        server_socket.sendto(response, address)


if __name__ == '__main__':
    run()
