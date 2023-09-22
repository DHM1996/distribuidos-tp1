from socket import socket

from src.lib.file_iterator import FileIterator
from src.lib.segment import Segment

class StopAndWaitProtocol:
    def __init__(self, socket, adress, timeout=1, retries=2):
        self.socket = socket
        self.adress = adress
        self.timeout = timeout
        self.max_tries = retries

    def send_file(self, file_path):
        file_iterator = FileIterator(file_path, Segment.DATA_SIZE)
        sequence_number = 0
        for segment_data in file_iterator:
            segment = Segment(sequence_number, segment_data)
            self.socket.sendto(segment.serialize(), self.adress)
            self.wait_ack(segment)
            sequence_number += 1

        fin_segment = Segment(sequence_number, fin=True)
        self.socket.sendto(fin_segment.serialize(), self.adress)
        self.wait_ack(fin_segment)

    def wait_ack(self, segment_to_ack: Segment):
        for _ in range(self.max_tries):
            try:
                # Wait for acknowledgment
                packet, _ = self.socket.recvfrom(Segment.MAX_SIZE)
                segment = Segment.deserialize(packet)
                if segment.is_ack() and segment.seq_ack_number == segment_to_ack.seq_ack_number:
                    return True
            except socket.timeout:
                self.socket.sendto(segment_to_ack.serialize(), self.adress)
        raise ConnectionError
