'''
Este protocolo intenta retransmitir únicamente aquellos paquetes que se sospechan que llegaron mal.
Para esto se utiliza una ventana de tamaño N que se usará para limitar el número de paquetes syn ACK del pipeline

Desde el lado del receptor, siempre se va a hacer ACK de los paquetes aunque no sea en orden.
Los paquetes fuera de orden irán al buffer hasta que los paquetes perdidos (aquellos que tienen número de secuencia menor) sean recibidos.
'''

import logging
import threading
import time
from typing import Optional

from file_iterator import FileIterator
from packet import Packet
from connection import Connection

logging.basicConfig(level=logging.INFO)


class SelectiveRepeatSender:
    def __init__(self, connection: Connection, window_size: int, timeout: float):
        self.connection = connection
        self.window_size = window_size
        self.timeout = timeout
        self.next_seq_num = 0
        self.base = 0
        self.timer = None
        self.buffer: list[Optional[Packet]] = [None] * window_size
        self.acked = [False] * window_size

    def start_threads(self):
        # Create two threads: one for sending and one for receiving
        # The sender thread will call the send_packets method of the sender object
        # The receiver thread will call the receive_ack method of the sender object
        sender_thread = threading.Thread(target=self.send_packets)
        receiver_thread = threading.Thread(target=self.receive_ack)

        # Start both threads
        sender_thread.start()
        receiver_thread.start()

        # Wait for both threads to finish
        sender_thread.join()
        receiver_thread.join()

    def send_file(self, file_path: str):
        file_iter = FileIterator(file_path, Packet.DATA_SIZE)
        for data in file_iter:
            # Wait until there is a free slot in the window
            while self.next_seq_num >= self.base + self.window_size:
                pass

            packet = Packet(self.next_seq_num, data=data)

            # Store the packet in the buffer
            index = self.next_seq_num % self.window_size
            self.buffer[index] = packet

            self.connection.send(packet)
            # Start the timer if it is the first packet in the window
            if self.base == self.next_seq_num:
                self.start_timer()
            self.next_seq_num += 1

        # Wait until all packets are acknowledged
        while self.base < self.next_seq_num:
            pass

        # Send a FIN packet
        fin_packet = Packet(self.next_seq_num, fin=True)
        index = self.next_seq_num % self.window_size
        self.buffer[index] = fin_packet
        self.connection.send(fin_packet)
        self.start_timer()


    def start_timer(self):
        # Cancel the previous timer if any
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.timeout_handler)
        self.timer.start()

    def timeout_handler(self):
        # Resend only the unacked packets in the window
        for i in range(self.base, self.next_seq_num):
            index = i % self.window_size
            if not self.acked[index]:
                packet = self.buffer[index]
                self.connection.send(packet)
        self.start_timer()

    def receive_ack(self):
        ack_packet = self.connection.receive()
        if ack_packet.is_ack():
            ack_number = ack_packet.get_seq_number()
            if self.base <= ack_number < self.next_seq_num:
                # Update the base of the window to the next expected ACK
                index = ack_number % self.window_size
                if not self.acked[index]:
                    self.acked[index] = True
                    while self.acked[self.base % self.window_size]: # Slide the window as long as there are consecutive ACKs at the front of the window
                        self.base += 1
                        if self.base == self.next_seq_num: # Stop the timer if the window is empty
                            break

                if not (self.base == self.next_seq_num):
                    self.start_timer()




class SelectiveRepeatReceiver:
    def __init__(self, connection: Connection, window_size: int):
        self.connection = connection
        self.expected_seq_num = 0
        self.window_size = window_size
        self.buffer = [None] * window_size

    def receive_file(self, file_path: str):
        file = open(file_path, 'wb')

        while True:
            packet = self.connection.receive()
            if packet.seq_number >= self.expected_seq_num and packet.seq_number < self.expected_seq_num + self.window_size:
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
                # FIN packet received, stop the loop
                break
            else:
                # Packet is outside the buffer range, discard it
                pass

            # Slide the window if possible
            while self.buffer[0]:
                self.expected_seq_num += 1
                file.write(self.buffer[0].data)
                del self.buffer[0]
                self.buffer.append(None)

        file.close()
