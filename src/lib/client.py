import logging
import socket
import sys

from src.conf.config import SERVER_IP, SERVER_PORT, CLIENT_FOLDER
from src.exceptions.client_exception import ClientException
from src.lib.connection import Connection
from src.lib.enums import Protocol, Action
from src.lib.packet import Packet
from src.lib.selective_repeat_protocol.selective_repeat_protocol import SelectiveRepeatProtocol
from src.lib.stop_and_wait_protocol import StopAndWaitProtocol

logging.basicConfig(level=logging.INFO)


class Client:

    def __init__(self, server_host, server_port, protocol: str):
        self.connection = Connection(host=server_host, port=server_port)

        if protocol == Protocol.STOP_AND_WAIT.value:
            self.protocol = StopAndWaitProtocol(self.connection)
        else:
            self.protocol = SelectiveRepeatProtocol(self.connection)

    @staticmethod
    def _create_socket():
        client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        logging.info("Socket created")
        return client_socket

    def _connect_with_server(self, action_to_run, file_name):
        logging.info("Trying to connect with server")
        data = f"{action_to_run},{file_name}".encode()
        packet = Packet(seq_number=0, syn=True, data=data)
        self.connection.send(packet)
        response = self.connection.receive()
        if response.is_ack():
            logging.info("Connection successfully established with server")
        else:
            logging.error(f"Connection with server failed: {response.get_data()}")

    def run(self, action_to_run, file_name):
        self._connect_with_server(action_to_run, file_name)

        file_path = f"{CLIENT_FOLDER}{file_name}"

        if action_to_run == Action.UPLOAD.value:
            self.protocol.send_file(file_path)

        elif action_to_run == Action.DOWNLOAD.value:
            self.protocol.receive_file(file_path)
        else:
            raise ClientException(f"Invalid action {action_to_run}")

        self.connection.close()
        logging.info("Socket closed")


if __name__ == '__main__':
    argv = sys.argv
    action = argv[1]
    file_name = argv[2]
    protocol_name = argv[3]
    client = Client(SERVER_IP, SERVER_PORT, protocol=protocol_name)
    client.run(action, file_name)
