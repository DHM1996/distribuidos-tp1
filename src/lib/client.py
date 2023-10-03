import logging
import os
import socket
from exceptions.connection_time_out_exception import ConnectionTimeOutException
from exceptions.server_exception import ServerException
from conf.config import MAX_CONNECTION_ATTEMPTS, TIMEOUT
from exceptions.client_exception import ClientException
from lib.connection import Connection
from lib.enums import Protocol, Action
from lib.packet import Packet
from lib.selective_repeat_protocol.selective_repeat_protocol import SelectiveRepeatProtocol
from lib.stop_and_wait_protocol import StopAndWaitProtocol


class Client:

    def __init__(self, server_host, server_port, protocol: Protocol):
        self.connection = Connection(host=server_host, port=server_port)

        if protocol.value == Protocol.STOP_AND_WAIT.value:
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

        for i in range(0, MAX_CONNECTION_ATTEMPTS):
            logging.info(f"Attempt: {i}")
            self.connection.send(packet)
            try:
                response = self.connection.receive(timeout=TIMEOUT)
                if response.is_ack() and response.data.decode() == "OK":
                    logging.info("Connection successfully established with server")
                    return
                else:
                    raise ServerException(response.data.decode())
            except ConnectionTimeOutException as err:
                continue
        raise ServerException("Connection to server failed")

    def run(self, action_to_run, file_src, file_name):

        file_path = f"{file_src}{file_name}"

        try:
            if action_to_run == Action.UPLOAD.value and not os.path.isfile(file_path):
                raise ClientException("File not found in client")

            self._connect_with_server(action_to_run, file_name)

            if action_to_run == Action.UPLOAD.value:
                self.protocol.send_file(file_path)

            elif action_to_run == Action.DOWNLOAD.value:
                self.protocol.receive_file(file_path)
            else:
                raise ClientException(f"Invalid action {action_to_run}")

            self.connection.close()
            logging.info("Socket closed")

        except Exception as err:
            logging.error(str(err))
            self.connection.close()
            exit(1)

        except KeyboardInterrupt as err:
            logging.error("El cliente detiene la acción voluntariamente ")
            self.connection.close()
            exit(1)
