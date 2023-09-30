from datetime import datetime
import logging
import queue
import threading
from socket import socket
from typing import Optional

from src.exceptions.connection_time_out import ConnectionTimeOut
from src.lib.file_iterator import FileIterator
from src.lib.packet import Packet


class SelectiveRepeatSender:
    def __init__(self, socket_: socket, dest_host, dest_port, window_size: int = 100, timeout: float = 1, max_tries=3,
                 recv_queue: queue.Queue = None):
        self.recv_queue = recv_queue
        self.socket = socket_
        self.dest_address = (dest_host, dest_port)
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
        self.package_timer: list = [None] * window_size

    def send_file(self, file_path: str, block=True):
        self.__send_file_start_threads(file_path, block)

    def __send_file_start_threads(self, file_path, block=True):
        # Create two threads: one for sending and one for receiving
        # The sender thread will call the send_packets method of the sender object
        # The receiver thread will call the receive_ack method of the sender object
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
                pass

            packet = Packet(self.next_seq_num, data=data)

            # Store the packet in the buffer
            index = self.next_seq_num % self.window_size
            self.buffer[index] = packet
            self.acked[index] = False
            self.package_timer[index] = (datetime.now(), 0)

            self.socket.sendto(packet.serialize(), self.dest_address)
            logging.info(f'Sent packet {self.next_seq_num}')
            self.next_seq_num += 1

        # Wait until all packets are acknowledged
        logging.info('Waiting for all packets to be acknowledged')
        while self.base < self.next_seq_num:
            pass

        # Send a FIN packet
        fin_packet = Packet(self.next_seq_num, fin=True)
        index = self.next_seq_num % self.window_size
        self.buffer[index] = fin_packet
        self.socket.sendto(fin_packet.serialize(), self.dest_address)
        logging.info(f'Sent FIN packet {self.next_seq_num}')
        self.is_finished = True

    def manage_package_timer(self):
        while not self.is_finished:
            for index, value in enumerate(self.package_timer):
                if value is None:
                    continue

                (packet_time, packet_try) = value
                time_delta = datetime.now() - packet_time
                time_delta_seconds = time_delta.total_seconds()

                if time_delta_seconds > self.timeout and self.buffer[index] is not None and not self.acked[index]:
                    if packet_try > self.max_tries:
                        raise ConnectionTimeOut("Packet max tries reached")

                    packet = self.buffer[index]
                    self.socket.sendto(packet.serialize(), self.dest_address)
                    packet_try += 1
                    self.package_timer[index] = (datetime.now(), packet_try)

    def receive_ack(self):
        logging.info('Started receiving ACKs')
        while True:
            try:
                ack_packet = self.receive_packet()
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
                    # Slide the window as long as there are consecutive ACKs at the front of the window
                    while self.acked[self.base % self.window_size] and not self.window_is_empty():
                        self.buffer[index] = None
                        self.acked[self.base % self.window_size] = False
                        self.base += 1

        logging.info('Finished receiving ACKs. Base: ' + str(self.base) + ', Next Seq Num: ' + str(self.next_seq_num))

    def window_is_empty(self):
        return self.base == self.next_seq_num

    def wait_threads(self):
        self.sender_thread.join()
        self.receiver_thread.join()

    def receive_packet(self):
        if self.recv_queue:
            packet: Packet = self.recv_queue.get(block=True)
            logging.info(f" Received packet with seq number {packet.seq_number} from queue")
        else:
            serialize_packet, address = self.socket.recvfrom(Packet.MAX_SIZE)
            packet: Packet = Packet.deserialize(serialize_packet)
            logging.info(f" Received packet with seq number {packet.seq_number} from thread")
        return packet
