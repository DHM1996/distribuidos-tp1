import queue
import socket
import logging

from conf.config import BUFFER_SIZE
from .file_iterator import FileIterator
from .packet import Packet

logging.basicConfig(level=logging.INFO)


class StopAndWaitProtocol:
    def __init__(self, socket_: socket.socket, dest_host, dest_port, recv_queue: queue.Queue = None, retries=2):
        self.dest_address = (dest_host, dest_port)
        self.socket = socket_
        self.recv_queue = recv_queue
        self.max_tries = retries + 1
        self.last_seq_num = -1

    def send_file(self, file_path):
        file_iterator = FileIterator(file_path, Packet.DATA_SIZE)

        seq_number = 0

        for packet_data in file_iterator:
            packet = Packet(seq_number, packet_data)
            self.send_packet(packet)
            seq_number += 1

        fin_packet = Packet(seq_number, fin=True)
        self.send_packet(fin_packet)

    def receive_file(self, file_path):
        logging.info(f"Receiving file in file path {file_path}")
        with open(file_path, "wb") as file:
            while True:
                packet = self.receive_packet()

                if packet.is_fin():
                    logging.info("Fin received")
                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.socket.sendto(ack_packet.serialize(), self.dest_address)
                    logging.info(f"ack sent for fin {packet.seq_number}")
                    break

                if packet.seq_number > self.last_seq_num:
                    file.write(packet.get_data())
                    self.last_seq_num = packet.seq_number

                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.socket.sendto(ack_packet.serialize(), self.dest_address)
                    logging.info(f"ack sent for package with seq number {packet.seq_number}")

            logging.info(f"File {file_path} received successfully")

    def receive_packet(self):
        if self.recv_queue:
            packet: Packet = self.recv_queue.get(block=True)
            logging.info(f" Received packet with seq number {packet.seq_number} from queue")
        else:
            serialize_packet, address = self.socket.recvfrom(Packet.MAX_SIZE)
            packet: Packet = Packet.deserialize(serialize_packet)
            logging.info(f" Received packet with seq number {packet.seq_number} from thread")
        return packet

    def send_packet(self, packet: Packet):
        for _ in range(self.max_tries):
            logging.info(f"packet with seq_number {packet.seq_number} sent")
            self.socket.sendto(packet.serialize(), self.dest_address)
            response = self.receive_packet()
            if response.is_ack() and response.seq_number == packet.seq_number:
                return
        raise ConnectionError
