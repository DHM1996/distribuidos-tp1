import logging
import queue
import select
import socket
from queue import Queue

from src.exceptions.connection_time_out_exception import ConnectionTimeOutException
from src.lib.packet import Packet


class Connection:
    def __init__(self, host: str, port: int, bind_ip: str = None, bind_port: int = None, reception_queue: Queue[Packet] = None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        if bind_ip is not None and bind_port is not None:
            self.socket.bind((bind_ip, bind_port))
        self.reception_queue = reception_queue

    def send(self, packet: Packet):
        self.socket.sendto(packet.serialize(), (self.host, self.port))

    def receive(self, timeout=None) -> Packet:
        if self.reception_queue is not None:
            try:
                packet = self.reception_queue.get(block=True, timeout=timeout)
            except queue.Empty:
                raise ConnectionTimeOutException("Queue timeout")
        else:
            if timeout:
                ready = select.select([self.socket], [], [], timeout if timeout else 0)
                if ready[0]:
                    packet, _ = self.socket.recvfrom(Packet.MAX_SIZE)
                    packet = Packet.deserialize(packet)
                else:
                    raise ConnectionTimeOutException("Socket timeout")
            else:
                packet, _ = self.socket.recvfrom(Packet.MAX_SIZE)
                packet = Packet.deserialize(packet)
        return packet

    def close(self):
        logging.info('Closing connection')
        self.socket.close()
