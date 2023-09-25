'''
Este protocolo intenta retransmitir únicamente aquellos paquetes que se sospechan que llegaron mal.
Para esto se utiliza una ventana de tamaño N que se usará para limitar el número de paquetes syn ACK del pipeline

Desde el lado del receptor, siempre se va a hacer ACK de los paquetes aunque no sea en orden.
Los paquetes fuera de orden irán al buffer hasta que los paquetes perdidos (aquellos que tienen número de secuencia menor) sean recibidos.
'''

import logging
import threading
import time
import random

from file_iterator import FileIterator
from packet import Packet
from connection import Connection

logging.basicConfig(level=logging.INFO)

class SelectiveRepeatSender:
    def __init__(self, connection, window_size, timeout):
        self.connection = connection
        self.window_size = window_size
        self.base = 0
        self.sequence_number = 0
        self.timer = {}
        self.timeout = timeout

    def send_file(self, file_path):
        file_iterator = FileIterator(file_path, Packet.DATA_SIZE)
        while self.base < file_iterator.get_length():
            if self.base + self.window_size > self.sequence_number < file_iterator.get_length():
                packet = Packet(self.sequence_number, file_iterator.get_part(self.sequence_number))
                self.connection.send(packet)
                self.timer[self.sequence_number] = time.time()
                if self.base == self.sequence_number:
                    threading.Thread(target=self.timer_thread(file_iterator)).start()
                self.sequence_number += 1
            else:
                time.sleep(0.1)


    def send_packet(self, seq_num, file_iterator):
        if time.time() - self.timer[seq_num] >= self.timeout:
            packet = Packet(self.sequence_number, file_iterator.get_part(self.sequence_number))
            self.connection.send(packet)
            self.timer[seq_num] = time.time()


    def timer_thread(self, file_iterator):
        while True:
            lost_packets = [seq_num for seq_num, timestamp in self.timer.items() if time.time() - timestamp >= self.timeout]
            for seq_num in self.timer.keys():
                self.send_packet(seq_num, file_iterator)
            for seq_num in lost_packets:
                self.send_packet(seq_num, file_iterator)



    def receive_ack(self):
        packet = self.connection.receive()
        if packet.is_ack() and packet.seq_number >= self.base:
            self.base = packet.seq_number + 1
            if self.base == self.sequence_number:
                # All packets in the current window have been acknowledged.
                self.timer = {}


class SelectiveRepeatReceiver:
    def __init__(self, connection):
        self.connection = connection
        self.expected_seq_num = 0

    def receive(self):
        while True:
            packet = self.connection.receive()
            if packet.seq_number == self.expected_seq_num:
                ack_packet = Packet(packet.seq_number, ack=True)
                self.connection.send(ack_packet)  # Send ACK
                self.expected_seq_num += 1
            elif packet.seq_number > self.expected_seq_num:
                # Out of order packet, discard it
                pass
