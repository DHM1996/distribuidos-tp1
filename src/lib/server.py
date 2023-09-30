import logging
import queue
import socket
import threading

from conf.config import SERVER_IP, SERVER_PORT, SERVER_FOLDER
from lib.enums import Protocol, Action
from lib.packet import Packet
from lib.stop_and_wait_protocol import StopAndWaitProtocol

from src.lib.selective_repeat_protocol.selective_repeat_protocol import SelectiveRepeatProtocol

logging.basicConfig(level=logging.INFO)

class Server:

    def __init__(self, host, port, protocol: Protocol):
        self.address = (host, port)
        self.socket = self._create_socket()
        self.clients = {}
        self.protocol = protocol

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
        file_path = f"{SERVER_FOLDER}{file_name}"

        logging.info(f"action: {action}, file_name: {file_name}")

        if self.protocol == Protocol.STOP_AND_WAIT:
            protocol = StopAndWaitProtocol(self.socket, dest_host, dest_port, self.clients[client_address])
        else:
            protocol = SelectiveRepeatProtocol(self.socket, dest_host, dest_port, self.clients[client_address])

        if action == Action.UPLOAD.value:
            protocol.receive_file(file_path)

        elif action == Action.DOWNLOAD.value:
            protocol.send_file(file_path)

        self.clients.pop(client_address)
        logging.info(f"Deleting queue for cliente with address {client_address}")

    def run(self):
        """ Handle Clients packets.
        If the packet is a sync, it creates a new queue for the cliente packets and a new thread to handle that cliente.
        If the packet is from an existent client, It adds the packet to the client's queue
        If the packet is from a no existent client and is not a sync, it sends an error response

        cliente queue: the queue where all the client packets are stored """

        logging.info("Listening...")

        while True:
            serialized_packet, client_address = self.socket.recvfrom(Packet.MAX_SIZE)
            packet: Packet = Packet.deserialize(serialized_packet)

            if packet.syn:

                if client_address not in self.clients.keys():
                    logging.info(f"New connection from client {client_address}")
                    threading.Thread(target=self.handle_new_client, args=(packet, client_address)).start()
                    response: packet = Packet(ack=True, seq_number=packet.seq_number, data="OK".encode())
                    self.socket.sendto(response.serialize(), client_address)

                else:
                    logging.info(f"Received a sync from existent client {client_address}. The connection was rejected")
                    self.socket.sendto("CONNECTION FAILED".encode(), client_address)

            else:
                logging.info(f"Received packet with seq_number {packet.seq_number} from {client_address}")
                client_queue: queue.Queue = self.clients.get(client_address)

                if client_queue:
                    logging.info(f"Adding packet with seq_number {packet.seq_number} from {client_address} to queue")
                    client_queue.put(packet)

                else:
                    logging.info(f"Received a packet without a previous syn from client {client_address}. "
                                 f"The connection was rejected")
                    self.socket.sendto("CONNECTION FAILED".encode(), client_address)


if __name__ == '__main__':
    server = Server(SERVER_IP, SERVER_PORT, Protocol.SELECTIVE_REPEAT)
    server.run()
