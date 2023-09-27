import logging
from typing import Optional

from src.lib.connection import Connection
from src.lib.packet import Packet


class SelectiveRepeatReceiver:
    def __init__(self, connection: Connection, window_size: int):
        self.connection = connection
        self.expected_seq_num = 0
        self.window_size = window_size
        self.buffer: list[Optional[Packet]] = [None] * window_size

    def receive_file(self, file_path):
        logging.info(f'Receiving file {file_path}')
        file = open(file_path, 'wb')

        while True:
            packet = self.connection.receive()
            logging.info(f'Received packet {packet.seq_number}')
            if self.expected_seq_num <= packet.seq_number < self.expected_seq_num + self.window_size:
                # Packet is within the window
                index = packet.seq_number - self.expected_seq_num
                if not self.buffer[index]:
                    # Packet has not been received before
                    self.buffer[index] = packet
                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.connection.send(ack_packet)  # Send ACK
                else:
                    # Packet has already been received, resend ACK
                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.connection.send(ack_packet)  # Send ACK
            elif packet.is_fin():
                logging.info('Received FIN packet')
                # FIN packet received, stop the loop
                break
            else:
                logging.info(f"Packet {packet.seq_number} is outside the window")
                # Packet is outside the buffer range, discard it
                pass

            # Slide the window if possible
            while self.buffer[0]:
                self.expected_seq_num += 1
                file.write(self.buffer[0].data)
                del self.buffer[0]
                self.buffer.append(None)

            logging.info(f'Slided expected sequence number to: {self.expected_seq_num}')

        file.close()
