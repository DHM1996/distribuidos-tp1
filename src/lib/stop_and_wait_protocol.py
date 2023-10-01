import logging

from conf.config import TIMEOUT
from .connection import Connection
from .file_iterator import FileIterator
from .packet import Packet
from ..exceptions.connection_time_out_exception import ConnectionTimeOutException


class StopAndWaitProtocol:
    def __init__(self, connection: Connection, retries=10, timeout=TIMEOUT):
        self.connection = connection
        self.max_tries = retries + 1
        self.last_seq_num = -1
        self.timeout = timeout

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
                packet = self.connection.receive(timeout=self.timeout * self.max_tries)

                if packet.is_fin():
                    logging.info("Fin received")
                    ack_packet = Packet(packet.seq_number, ack=True)
                    self.connection.send(ack_packet)
                    logging.info(f"ack sent for fin {packet.seq_number}")
                    break

                if packet.seq_number > self.last_seq_num:
                    file.write(packet.get_data())
                    self.last_seq_num = packet.seq_number

                ack_packet = Packet(packet.seq_number, ack=True)
                self.connection.send(ack_packet)
                logging.info(f"ack sent for package with seq number {packet.seq_number}")

            logging.info(f"File {file_path} received successfully")

    def send_packet(self, packet: Packet):
        for _ in range(self.max_tries):
            logging.info(f"packet with seq_number {packet.seq_number} sent")
            self.connection.send(packet)
            try:
                response = self.connection.receive(timeout=self.timeout)
                if response.is_ack() and response.seq_number == packet.seq_number:
                    return
            except ConnectionTimeOutException:
                logging.info(f"Timeout with seq_number {packet.seq_number}")
                continue
        raise ConnectionTimeOutException(f"Action Failed: Connection timed out with seq_number {packet.seq_number}")
