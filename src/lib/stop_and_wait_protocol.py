import select
import socket
import logging

from .file_iterator import FileIterator
from .segment import Segment

logging.basicConfig(level=logging.INFO)

class StopAndWaitProtocol:
    def __init__(self, socket, address, timeout=1, retries=2):
        self.socket = socket
        self.address = address
        self.timeout = timeout
        self.max_tries = retries
        self.last_seq_num = 0

    def send_file(self, file_path):
        file_iterator = FileIterator(file_path, Segment.DATA_SIZE)
        sequence_number = 0
        for segment_data in file_iterator:
            segment = Segment(sequence_number, segment_data)
            self.socket.sendto(segment.serialize(), self.address)
            self.wait_ack(segment)
            sequence_number += 1

        fin_segment = Segment(sequence_number, fin=True)
        self.socket.sendto(fin_segment.serialize(), self.address)
        self.wait_ack(fin_segment)

    def receive_to_file(self, file_path):
        with open(file_path, "wb") as file:
            while True:
                try:
                    # Receive segment
                    ready = select.select([self.socket], [], [], self.timeout)
                    if ready[0]:
                        segment = Segment.receive_from(self.socket)
                    else:
                        raise socket.timeout

                    # If new segment, write data to file and update sequence number
                    if segment.seq_ack_number > self.last_seq_num:
                        file.write(segment.get_data())
                        self.last_seq_num = segment.seq_ack_number

                    # Send acknowledgement
                    response = Segment(segment.seq_ack_number, ack=True)
                    self.socket.sendto(response.serialize(), self.address)

                    # If FIN packet received, break the loop
                    if segment.is_fin():
                        logging.info(f"StopAndWaitProtocol: FIN packet received from {self.address}")
                        break

                except socket.timeout:
                    logging.info(f"StopAndWaitProtocol: Connection timed out for address {self.address}")
                    raise ConnectionError

        logging.info(f"StopAndWaitProtocol: File successfully downloaded to {file_path} from {self.address}")

    def wait_ack(self, segment_to_ack: Segment):
        for _ in range(self.max_tries):
            try:
                # Wait for acknowledgment
                segment = Segment.receive_from(self.socket)
                if segment.is_ack() and segment.seq_ack_number == segment_to_ack.seq_ack_number:
                    return True
            except socket.timeout:
                self.socket.sendto(segment_to_ack.serialize(), self.address)
        raise ConnectionError
