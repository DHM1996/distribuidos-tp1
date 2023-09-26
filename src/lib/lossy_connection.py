import select
import socket
from random import random

from packet import Packet
from src.lib.connection import Connection


class LossyConnection(Connection):
    def __init__(self, ip: str, port: int, timeout: float, loss_rate: float):
        super().__init__(ip, port, timeout)
        self.loss_rate = loss_rate

    def set_loss_rate(self, loss_rate: float):
        self.loss_rate = loss_rate

    def send(self, packet: Packet):
        if random() > self.loss_rate:
            super().send(packet)
