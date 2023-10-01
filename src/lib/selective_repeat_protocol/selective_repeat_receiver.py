import logging
from typing import Optional

from src.lib.connection import Connection
from src.lib.packet import Packet


class SelectiveRepeatReceiver:
    def __init__(self, connection: Connection, window_size: int = 100):
        self.connection = connection
        self.expected_seq_num = 0
        self.window_size = window_size
        self.buffer: list[Optional[Packet]] = [None] * window_size

    def receive_file(self, file_path):
        logging.info(f'Receiving file {file_path}')
        file = open(file_path, 'wb')

        while True:
            packet = self.connection.receive()
            logging.debug(f'Received packet {packet.seq_number}')
            if packet.is_fin():
                logging.info('Received FIN packet')
                ack_fin_packet = Packet(packet.seq_number, ack=True, fin=True)
                self.connection.send(ack_fin_packet)  # Send ACK
                # FIN packet received, stop the loop
                break

            index = packet.seq_number - self.expected_seq_num
            if self.is_in_window(packet.seq_number) and not self.buffer[index]:
                # Packet has not been received before
                self.buffer[index] = packet

            logging.debug(f'Sending ACK for packet {packet.seq_number}')
            ack_packet = Packet(packet.seq_number, ack=True)
            self.connection.send(ack_packet)  # Send ACK

            # Slide the window if possible
            while self.buffer[0]:
                self.expected_seq_num += 1
                file.write(self.buffer[0].data)
                del self.buffer[0]
                self.buffer.append(None)

                logging.info(f'Slided expected sequence number to: {self.expected_seq_num}')

        file.close()

    def is_in_window(self, seq_number: int) -> bool:
        return self.expected_seq_num <= seq_number < self.expected_seq_num + self.window_size
