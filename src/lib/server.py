import logging
import os
import queue
import socket
import threading

from conf.config import SERVER_IP, SERVER_PORT, SERVER_FOLDER
from lib.connection import Connection
from lib.enums import Protocol, Action
from lib.packet import Packet
from lib.selective_repeat_protocol.selective_repeat_protocol import SelectiveRepeatProtocol
from lib.stop_and_wait_protocol import StopAndWaitProtocol


class Server:
    def __init__(self, host, port, protocol: Protocol, server_folder):
        self.address = (host, port)
        self.socket = self._create_socket()
        self.clients = {}
        self.protocol = protocol
        self.server_folder = server_folder

    def _create_socket(self):
        """ Create a new UDP socket in the server host and port """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(self.address)
        logging.info(f"Server socket created with address {self.address}")
        return server_socket

    def handle_new_client(self, packet, client_address):
        self.clients[client_address] = queue.Queue()
        dest_host, dest_port = client_address

        data = packet.get_data().decode()
        action, file_name = data.split(",")

        file_path = f"{self.server_folder}{file_name}"

        logging.info(f"action: {action}, file_name: {file_name}")

        if action == Action.DOWNLOAD.value and not os.path.isfile(file_path):
            logging.error(f"File not found: {file_path}")
            response: packet = Packet(ack=True, seq_number=packet.seq_number, data="File not Found".encode())
            self.socket.sendto(response.serialize(), client_address)
            return

        response: packet = Packet(ack=True, seq_number=packet.seq_number, data="OK".encode())
        self.socket.sendto(response.serialize(), client_address)

        connection = Connection(host=dest_host, port=dest_port, reception_queue=self.clients[client_address])

        if self.protocol.value == Protocol.STOP_AND_WAIT.value:
            protocol = StopAndWaitProtocol(connection)
        else:
            protocol = SelectiveRepeatProtocol(connection)

        if action == Action.UPLOAD.value:
            protocol.receive_file(file_path)

        elif action == Action.DOWNLOAD.value:
            protocol.send_file(file_path)

        connection.close()
        self.clients.pop(client_address)
        logging.info(f"Deleting queue for cliente with address {client_address}")

    def run(self):
        """ Handle Clients packets.
        If the packet is a sync, it creates a new queue for the cliente packets and a new thread to handle that cliente.
        If the packet is from an existent client, It adds the packet to the client's queue
        If the packet is from a no existent client and is not a sync, it sends an error response

        cliente queue: the queue where all the client packets are stored """

        logging.info("Listening...")

        try:

            while True:
                serialized_packet, client_address = self.socket.recvfrom(Packet.MAX_SIZE)
                packet: Packet = Packet.deserialize(serialized_packet)

                if packet.syn:

                    if client_address not in self.clients.keys():
                        logging.info(f"New connection from client {client_address}")
                        threading.Thread(target=self.handle_new_client, args=(packet, client_address)).start()
                    else:
                        message = f"Received a sync from existent client {client_address}. The connection was rejected"
                        logging.info(message)
                        self.socket.sendto(Packet(seq_number=packet.seq_number, ack=True, data=message.encode())
                                           .serialize(), client_address)

                else:
                    logging.info(f"Received packet with seq_number {packet.seq_number} from {client_address}")
                    client_queue: queue.Queue = self.clients.get(client_address)

                    if client_queue:
                        logging.info(
                            f"Adding packet with seq_number {packet.seq_number} from {client_address} to queue")
                        client_queue.put(packet)

                    else:
                        message = f"Received a packet without a previous syn from client {client_address}. "
                        f"The connection was rejected"
                        logging.info(message)
                        self.socket.sendto(Packet(seq_number=packet.seq_number, ack=True, data=message.encode())
                                           .serialize(), client_address)

        except KeyboardInterrupt:
            logging.error("El servidor fue interrumpido por el usuario. Se cierra el socket.")
            self.socket.close()
            exit(1)
