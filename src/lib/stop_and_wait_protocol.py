import select
import socket
import logging

from .connection import Connection
from .file_iterator import FileIterator
from .packet import Packet

logging.basicConfig(level=logging.INFO)

class StopAndWaitProtocol:
    def __init__(self, connection, retries=2):
        self.connection = connection
        self.max_tries = retries + 1
        self.last_seq_num = 0

    def send_file(self, file_path):
        file_iterator = FileIterator(file_path, Packet.DATA_SIZE)
        sequence_number = 0
        for packet_data in file_iterator:
            packet = Packet(sequence_number, packet_data)
            self.connection.send(packet)
            self.wait_ack(packet)
            sequence_number += 1

        fin_packet = Packet(sequence_number, fin=True)
        self.connection.send(fin_packet)
        self.wait_ack(fin_packet)

    def receive_to_file(self, file_path):
        with open(file_path, "wb") as file:
            while True:
                try:
                    # Receive packet
                    packet = self.connection.receive()

                    # If new packet, write data to file and update sequence number
                    if packet.seq_number > self.last_seq_num:
                        file.write(packet.get_data())
                        self.last_seq_num = packet.seq_number

                    # Send acknowledgement
                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.connection.send(ack_packet)

                    # If FIN packet received, break the loop
                    if packet.is_fin():
                        logging.info(f"StopAndWaitProtocol: FIN packet received from {self.connection.address}")
                        break

                except socket.timeout:
                    logging.info(f"StopAndWaitProtocol: Connection timed out for address {self.connection.address}")
                    raise ConnectionError

        logging.info(f"StopAndWaitProtocol: File successfully downloaded to {file_path} from {self.connection.address}")

    def wait_ack(self, packet_to_ack: Packet):
        for _ in range(self.max_tries):
            try:
                # Wait for acknowledgment
                packet = self.connection.receive()
                if packet.is_ack() and packet.seq_number == packet_to_ack.seq_number:
                    return True
            except socket.timeout:
                self.connection.send(packet_to_ack)
        raise ConnectionError
