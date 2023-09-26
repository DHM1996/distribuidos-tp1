from random import random

from .packet import Packet
from src.lib.connection import Connection


class LossyConnection(Connection):
    def __init__(self, ip: str, port: int, timeout: float, loss_rate: float, bind_ip: str = None, bind_port: int = None):
        super().__init__(ip, port, timeout, bind_ip, bind_port)
        self.loss_rate = loss_rate

    def set_loss_rate(self, loss_rate: float):
        self.loss_rate = loss_rate

    def send(self, packet: Packet):
        if random() > self.loss_rate:
            super().send(packet)
