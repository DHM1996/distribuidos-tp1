import logging
import socket
import sys

from conf.config import SERVER_IP, SERVER_PORT, CLIENT_FOLDER
from exceptions.client_exception import ClientException
from lib.enums import Action, Protocol
from lib.packet import Packet
from lib.stop_and_wait_protocol import StopAndWaitProtocol

logging.basicConfig(level=logging.INFO)


class Client:

    def __init__(self, server_host, server_port, protocol: Protocol):
        self.server_address = (server_host, server_port)
        self.socket = self._create_socket()

        if protocol == Protocol.STOP_AND_WAIT:
            self.protocol = StopAndWaitProtocol(self.socket, server_host, server_port)
        else:
            # ToDo change for selective repeat
            self.protocol = StopAndWaitProtocol(self.socket, server_host, server_port)

    @staticmethod
    def _create_socket():
        client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        logging.info("Socket created")
        return client_socket

    def _connect_with_server(self, action, file_name):
        logging.info("Trying to connect with server")
        data = f"{action},{file_name}".encode()
        packet: Packet = Packet(seq_number=0, syn=True, data=data)
        serialized_packet = packet.serialize()
        self.socket.sendto(serialized_packet, self.server_address)
        serialized_response, address = self.socket.recvfrom(Packet.MAX_SIZE)
        response = Packet.deserialize(serialized_response)
        if response.ack:
            logging.info("Connection successfully established with server")
        else:
            logging.error(f"Connection with server failed: {response.get_data()}")

    def run(self, action, file_name):
        self._connect_with_server(action, file_name)

        file_path = f"{CLIENT_FOLDER}{file_name}"

        if action == Action.UPLOAD.value:
            self.protocol.send_file(file_path)

        elif action == Action.DOWNLOAD.value:
            self.protocol.receive_file(file_path)
        else:
            raise ClientException(f"Invalid action {action}")

        self.socket.close()
        logging.info("Socket closed")


if __name__ == '__main__':
    argv = sys.argv
    action = argv[1]
    file_name = argv[2]
    client = Client(SERVER_IP, SERVER_PORT, protocol=Protocol.STOP_AND_WAIT)
    client.run(action, file_name)
