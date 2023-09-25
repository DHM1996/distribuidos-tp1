import select
import socket
from random import random

from packet import Packet


class LossyConnection:
    def __init__(self, connection_socket: socket, ip: str, port: int, timeout: float, loss_rate: float):
        self.connection_socket = connection_socket
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.loss_rate = loss_rate

    def set_loss_rate(self, loss_rate: float):
        self.loss_rate = loss_rate

    def set_timeout(self, timeout: float):
        self.timeout = timeout

    def send(self, packet: Packet):
        if random() > self.loss_rate:
            self.connection_socket.sendto(packet.serialize(), (self.ip, self.port))

    def receive(self) -> Packet:
        ready = select.select([self.connection_socket], [], [], self.timeout)
        if ready[0]:
            packet, _ = self.connection_socket.recvfrom(Packet.MAX_SIZE)
        else:
            raise socket.timeout
        return packet.deserialize()

    def close(self):
        self.connection_socket.close()