import logging
import queue
import socket
from typing import Optional

from src.lib.connection import Connection
from src.lib.packet import Packet


class SelectiveRepeatReceiver:
    def __init__(self, socket_: socket, dest_host, dest_port, window_size: int = 10, recv_queue: queue.Queue = None):
        self.recv_queue = recv_queue
        self.socket = socket_
        self.dest_address = (dest_host, dest_port)
        self.expected_seq_num = 0
        self.window_size = window_size
        self.buffer: list[Optional[Packet]] = [None] * window_size

    def receive_file(self, file_path):
        logging.info(f'Receiving file {file_path}')
        file = open(file_path, 'wb')

        while True:
            packet = self.receive_packet()
            logging.info(f'Received packet {packet.seq_number}')
            if packet.is_fin():
                logging.info('Received FIN packet')
                ack_fin_packet = Packet(packet.seq_number, ack=True, fin=True)
                self.socket.sendto(ack_fin_packet.serialize(), self.dest_address)  # Send ACK
                # FIN packet received, stop the loop
                break
            elif self.expected_seq_num <= packet.seq_number < self.expected_seq_num + self.window_size:
                # Packet is within the window
                index = packet.seq_number - self.expected_seq_num
                if not self.buffer[index]:
                    # Packet has not been received before
                    self.buffer[index] = packet
                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.socket.sendto(ack_packet.serialize(), self.dest_address)  # Send ACK
                else:
                    # Packet has already been received, resend ACK
                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.socket.sendto(ack_packet.serialize(), self.dest_address)  # Send ACK
            else:
                logging.info(f"Packet {packet.seq_number} is outside the window, resend ACK")
                # Packet is outside the buffer range, resend ACK, maybe the first ACK was lost
                ack_packet = Packet(packet.seq_number, ack=True)
                self.socket.sendto(ack_packet.serialize(), self.dest_address)  # Send ACK

            # Slide the window if possible
            while self.buffer[0]:
                self.expected_seq_num += 1
                file.write(self.buffer[0].data)
                del self.buffer[0]
                self.buffer.append(None)

            logging.info(f'Slided expected sequence number to: {self.expected_seq_num}')

        file.close()

    def receive_packet(self):
        if self.recv_queue:
            packet: Packet = self.recv_queue.get(block=True)
            logging.info(f" Received packet with seq number {packet.seq_number} from queue")
        else:
            serialize_packet, address = self.socket.recvfrom(Packet.MAX_SIZE)
            packet: Packet = Packet.deserialize(serialize_packet)
            logging.info(f" Received packet with seq number {packet.seq_number} from thread")
        return packet
