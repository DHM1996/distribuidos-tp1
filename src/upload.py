import socket
from src.start_server import SERVER_IP, SERVER_PORT

CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 8081
BUFFER_SIZE = 1024


def run():
    client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    message = str.encode("Te envio un mensage")

    client_socket.sendto(message, (SERVER_IP, SERVER_PORT))

    response, address = client_socket.recvfrom(BUFFER_SIZE)

    print("Message from Server {}".format(response))


if __name__ == '__main__':
    run()
