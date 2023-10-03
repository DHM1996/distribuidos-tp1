import os
import time
import logging
import threading
from typing import Union, Optional

from exceptions.closed_socket_exception import ClosedSocketException
from exceptions.connection_time_out_exception import ConnectionTimeOutException
from lib.connection import Connection
from lib.file_iterator import FileIterator
from lib.packet import Packet


class SelectiveRepeatSender:
    def __init__(self, connection: Connection, window_size: int = 30, timeout: float = 1, max_tries=10):
        self.connection = connection
        self.window_size = window_size
        self.timeout = timeout
        self.next_seq_num = 0
        self.base = 0
        self.timer = None
        self.buffer: list[Optional[list]] = [None] * window_size
        self.is_finished = False
        self.sender_thread = None
        self.receiver_thread = None
        self.max_tries = max_tries
        self.try_number = 0
        self.is_timed_out = False

    def send_file(self, file_path: Union[str, os.PathLike], block):
        self.__send_file_start_threads(file_path, block)

    def __send_file_start_threads(self, file_path, block=True):
        # Create three threads: one for sending packets, one for receiving ACKs and one for managing the package timer
        # The sender thread will call the send_packets method of the sender object
        # The receiver thread will call the receive_ack method of the sender object
        # The timer thread will call the manage_package_timer method of the sender object
        self.sender_thread = threading.Thread(target=self.__send_file, args=[file_path])
        self.receiver_thread = threading.Thread(target=self.receive_ack)
        self.timer = threading.Thread(target=self.manage_package_timer)

        # Start both threads
        self.sender_thread.start()
        self.receiver_thread.start()
        self.timer.start()
        logging.info('Started sender and receiver threads')

        if block:
            # Wait for both threads to finish
            self.sender_thread.join()
            self.receiver_thread.join()
            self.timer.join()

    def __send_file(self, file_path: str):

        file_iter = FileIterator(file_path, Packet.DATA_SIZE)
        for data in file_iter:
            logging.info(f'Sending packet {self.next_seq_num}')
            # Wait until there is a free slot in the window
            while self.next_seq_num >= self.base + self.window_size:
                if self.is_timed_out:
                    return
                pass

            packet = Packet(self.next_seq_num, data=data)

            # Store the packet in the buffer
            index = self.next_seq_num % self.window_size
            self.buffer[index] = [packet, False, (time.perf_counter(), 0)]
            try:
                self.connection.send(packet)
            except ClosedSocketException:
                return
            logging.info(f'Sent packet {self.next_seq_num}')
            self.next_seq_num += 1

        # Wait until all packets are acknowledged
        logging.info('Waiting for all packets to be acknowledged')
        while self.base < self.next_seq_num:
            if self.is_timed_out:
                return
            pass

        # Send a FIN packet
        fin_packet = Packet(self.next_seq_num, fin=True)
        index = self.next_seq_num % self.window_size
        self.buffer[index] = [fin_packet, False, (time.perf_counter(), 0)]
        self.connection.send(fin_packet)
        logging.info(f'Sent FIN packet {self.next_seq_num}')

    def manage_package_timer(self):
        while not self.is_finished:
            time.sleep(self.timeout / 4)
            for index, value in enumerate(self.buffer):
                if value is None:
                    continue

                (packet, is_ack, (packet_time, packet_try)) = value
                delta_seconds = time.perf_counter() - packet_time

                if (not is_ack) and delta_seconds > self.timeout:
                    if packet_try > self.max_tries:
                        logging.info(f'Packet {packet.get_seq_number()} timed out')
                        self.is_timed_out = True
                        return#raise ConnectionTimeOutException("Packet max tries reached")

                    logging.info(f'Resending packet {packet.get_seq_number()}')
                    try:
                        self.connection.send(packet)
                    except ClosedSocketException:
                        return
                    packet_try += 1
                    try:
                        self.buffer[index][2] = (time.perf_counter(), packet_try)
                    except TypeError:
                        continue
        logging.info('Finished managing package timer')

    def receive_ack(self):
        logging.info('Started receiving ACKs')
        while True:
            try:
                ack_packet = self.connection.receive(timeout=self.timeout * self.max_tries)
            except ConnectionTimeOutException:
               break
            except ClosedSocketException:
                return
            if ack_packet.is_fin():
                self.is_finished = True
                break
            ack_number = ack_packet.get_seq_number()
            logging.info(f'Received ACK packet {ack_packet.get_seq_number()}')
            if ack_packet.is_ack() and self.base <= ack_number < self.next_seq_num:
                index = ack_number % self.window_size
                if self.buffer[index] and not self.buffer[index][1]:
                    self.buffer[index][1] = True
                    # Slide the window as long as there are consecutive ACKs at the front of the window
                    while self.buffer[self.base % self.window_size] and self.buffer[self.base % self.window_size][1] and not self.window_is_empty():
                        self.buffer[self.base % self.window_size] = None
                        self.base += 1

        logging.info('Finished receiving ACKs. Base: ' + str(self.base) + ', Next Seq Num: ' + str(self.next_seq_num))

    def window_is_empty(self):
        return self.base == self.next_seq_num

    def wait_threads(self):
        self.sender_thread.join()
        self.receiver_thread.join()
