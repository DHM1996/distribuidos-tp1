'''
Este protocolo intenta retransmitir únicamente aquellos paquetes que se sospechan que llegaron mal.
Para esto se utiliza una ventana de tamaño N que se usará para limitar el número de paquetes syn ACK del pipeline

Desde el lado del receptor, siempre se va a hacer ACK de los paquetes aunque no sea en orden.
Los paquetes fuera de orden irán al buffer hasta que los paquetes perdidos (aquellos que tienen número de secuencia menor) sean recibidos.
'''

import socket
import threading
import time

from src.lib.file_iterator import FileIterator
from src.lib.segment import Segment


class SelectiveRepeatSender:
    def __init__(self, socket, address, window_size, timeout=1):
        self.socket = socket
        self.address = address
        self.window_size = window_size
        self.base = 0
        self.sequence_number = 0
        self.timer = {}
        self.timeout = timeout

    def send_file(self, file_path):
        file_iterator = FileIterator(file_path, Segment.DATA_SIZE)
        while self.base < file_iterator.get_length():
            if self.base + self.window_size > self.sequence_number < file_iterator.get_length():
                segment = Segment(self.sequence_number, file_iterator.get_part(self.sequence_number))
                self.socket.sendto(segment.serialize(), self.address)
                self.timer[self.sequence_number] = time.time()
                if self.base == self.sequence_number:
                    threading.Thread(target=self.timer_thread).start()
                self.sequence_number += 1
            else:
                time.sleep(0.1)

    def timer_thread(self, data):
        while True:
            for seq_num in self.timer:
                if time.time() - self.timer[seq_num] >= self.timeout:
                    segment = Segment(self.sequence_number, data[self.sequence_number])
                    self.socket.sendto(segment.serialize(), self.address)
                    self.timer[seq_num] = time.time()

    def receive_ack(self):
        ack, _ = self.socket.recvfrom(1024)
        ack_num = int(ack.decode())
        if ack_num >= self.base:
            self.base = ack_num + 1
            if self.base == self.sequence_number:
                # All packets in the current window have been acknowledged.
                self.timer = {}


class SelectiveRepeatReceiver:
    def __init__(self, socket, address):
        self.address = address
        self.socket = socket
        self.expected_seq_num = 0

    def receive(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            seq_num = int(data.decode())
            if seq_num == self.expected_seq_num:
                self.socket.sendto(str(seq_num).encode(), addr)  # Send ACK
                self.expected_seq_num += 1
            elif seq_num > self.expected_seq_num:
                # Out of order packet, discard it
                pass
