import logging
import threading
from socket import socket
from typing import Optional

from src.exceptions.connection_time_out import ConnectionTimeOut
from src.lib.connection import Connection
from src.lib.file_iterator import FileIterator
from src.lib.packet import Packet


class SelectiveRepeatSender:
    def __init__(self, connection: Connection, window_size: int, timeout: float, max_tries=3):
        self.connection = connection
        self.window_size = window_size
        self.timeout = timeout
        self.next_seq_num = 0
        self.base = 0
        self.timer = None
        self.buffer: list[Optional[Packet]] = [None] * window_size
        self.acked = [False] * window_size
        self.is_finished = False
        self.sender_thread = None
        self.receiver_thread = None
        self.max_tries = max_tries
        self.try_number = 0

    def send_file(self, file_path: str, block=True):
        self.__send_file_start_threads(file_path, block)

    def __send_file_start_threads(self, file_path, block=True):
        # Create two threads: one for sending and one for receiving
        # The sender thread will call the send_packets method of the sender object
        # The receiver thread will call the receive_ack method of the sender object
        self.sender_thread = threading.Thread(target=self.__send_file, args=[file_path])
        self.receiver_thread = threading.Thread(target=self.receive_ack)

        # Start both threads
        self.sender_thread.start()
        self.receiver_thread.start()
        logging.info('Started sender and receiver threads')

        if block:
            # Wait for both threads to finish
            self.sender_thread.join()
            self.receiver_thread.join()

    def __send_file(self, file_path: str):
        file_iter = FileIterator(file_path, Packet.DATA_SIZE)
        for data in file_iter:
            logging.info(f'Sending packet {self.next_seq_num}')
            # Wait until there is a free slot in the window
            while self.next_seq_num >= self.base + self.window_size:
                pass

            packet = Packet(self.next_seq_num, data=data)

            # Store the packet in the buffer
            index = self.next_seq_num % self.window_size
            self.buffer[index] = packet
            self.acked[index] = False

            self.connection.send(packet)
            logging.info(f'Sent packet {self.next_seq_num}')
            # Start the timer if it is the first packet in the window
            if self.window_is_empty():
                logging.info(f'Starting timer for packet {self.next_seq_num}')
                self.start_timer()
            self.next_seq_num += 1

        # Wait until all packets are acknowledged
        logging.info('Waiting for all packets to be acknowledged')
        while self.base < self.next_seq_num:
            pass

        # Send a FIN packet
        fin_packet = Packet(self.next_seq_num, fin=True)
        index = self.next_seq_num % self.window_size
        self.buffer[index] = fin_packet
        self.connection.send(fin_packet)
        logging.info(f'Sent FIN packet {self.next_seq_num}')
        self.is_finished = True
        self.timer.cancel()

    def start_timer(self):
        if self.try_number >= self.max_tries:
            raise ConnectionTimeOut("Max tries reached")
        self.try_number += 1
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
                logging.info(f'Resent packet {packet.get_seq_number()}')
        self.start_timer()

    def receive_ack(self):
        logging.info('Started receiving ACKs')
        while True:
            try:
                ack_packet = self.connection.receive()
            except socket.timeout:
                if self.is_finished:
                    break
                else:
                    raise socket.timeout
            if ack_packet.is_fin():
                break
            ack_number = ack_packet.get_seq_number()
            logging.info(f'Received ACK packet {ack_packet.get_seq_number()}')
            if ack_packet.is_ack() and self.base <= ack_number < self.next_seq_num:
                index = ack_number % self.window_size
                if not self.acked[index]:
                    self.acked[index] = True
                    while self.acked[self.base % self.window_size] and not self.window_is_empty():  # Slide the window as long as there are
                        # consecutive ACKs at the front of the window
                        self.acked[self.base % self.window_size] = False
                        self.base += 1
                        self.try_number = 0
                        self.start_timer()
        logging.info('Finished receiving ACKs. Base: ' + str(self.base) + ', Next Seq Num: ' + str(self.next_seq_num))


    def window_is_empty(self):
        return self.base == self.next_seq_num

    def wait_threads(self):
        self.sender_thread.join()
        self.receiver_thread.join()