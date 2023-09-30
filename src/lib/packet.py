import struct


class Packet:
    MAX_SIZE = 4 * 1024
    HEADER_SIZE = 7
    DATA_SIZE = MAX_SIZE - HEADER_SIZE

    def __init__(self, seq_number, data=b'', syn=False, ack=False, fin=False):
        if len(data) > Packet.DATA_SIZE:
            raise ValueError("Segment data too large")
        self.seq_number = seq_number
        self.syn = syn
        self.ack = ack
        self.fin = fin
        self.data = data

    def is_syn(self):
        return self.syn

    def is_ack(self):
        return self.ack

    def is_fin(self):
        return self.fin

    def get_seq_number(self):
        return self.seq_number

    def get_data(self):
        return self.data

    def checksum(self):
        """
        Calculate and return a checksum of the data.
        """
        if not self.data:  # if data is empty return 0
            return 0

        data = self.data

        checksum = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                temp_data = data[i] + (data[i + 1] << 8)
                checksum += temp_data
                checksum = (checksum & 0xffff) + (checksum >> 16)

        return ~checksum & 0xffff

    def serialize(self):
        """
        Convert the Segment object into a binary format.
        """
        header = struct.pack('!I???', self.seq_number, self.syn, self.ack, self.fin)

        if self.data:
            return header + self.data

        return header

    @classmethod
    def deserialize(cls, data):
        """
        Convert a binary string back into a Segment object.
        """
        seq_number, syn, ack, fin = struct.unpack('!I???', data[:7])

        data = data[7:]

        return cls(seq_number=seq_number, data=data, syn=syn, ack=ack, fin=fin)
