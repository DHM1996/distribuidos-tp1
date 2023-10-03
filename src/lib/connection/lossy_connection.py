from random import random

from lib.packet import Packet
from lib.connection import Connection


class LossyConnection(Connection):
    def __init__(self, host: str, port: int, loss_rate: float, bind_ip: str = None, bind_port: int = None):
        super().__init__(host, port, bind_ip, bind_port)
        self.loss_rate = loss_rate

    def set_loss_rate(self, loss_rate: float):
        self.loss_rate = loss_rate

    def send(self, packet: Packet):
        if random() > self.loss_rate:
            super().send(packet)
