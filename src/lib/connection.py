import logging
import select
import socket

from .packet import Packet


class Connection:
    def __init__(self, ip: str, port: int, timeout: float, bind_ip: str = None, bind_port: int = None):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip = ip
        self.port = port
        self.timeout = timeout
        if bind_ip is not None and bind_port is not None:
            self.connection_socket.bind((bind_ip, bind_port))

    def send(self, packet: Packet):
        self.connection_socket.sendto(packet.serialize(), (self.ip, self.port))

    def receive(self) -> Packet:
        ready = select.select([self.connection_socket], [], [], self.timeout)
        if ready[0]:
            packet, _ = self.connection_socket.recvfrom(Packet.MAX_SIZE)
        else:
            raise socket.timeout
        return Packet.deserialize(packet)

    def close(self):
        logging.info('Closing connection')
        self.connection_socket.close()