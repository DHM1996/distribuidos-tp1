import select
import socket

from packet import Packet


class Connection:
    def __init__(self, ip: str, port: int, timeout: float):
        self.connection_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def send(self, packet: Packet):
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