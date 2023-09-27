import struct


class Packet:
    MAX_SIZE = 4 * 1024
    HEADER_SIZE = 5
    DATA_SIZE = MAX_SIZE - HEADER_SIZE
    def __init__(self, seq_number, data=b"", syn=False, ack=False, fin=False):
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

        checksum = 0
        for i in range(0, len(self.data), 2):
            if i + 1 < len(self.data):
                temp_data = self.data[i] + (self.data[i + 1] << 8)
                checksum += temp_data
                checksum = (checksum & 0xffff) + (checksum >> 16)

        return ~checksum & 0xffff

    def serialize(self):
        """
        Convert the Segment object into a binary format.
        """
        flags = (self.syn << 2) | (self.ack << 1) | self.fin
        header = struct.pack('!IB', self.seq_number, flags)
        return header + self.data

    @classmethod
    def deserialize(cls, data):
        """
        Convert a binary string back into a Segment object.
        """
        header = struct.unpack('!IB', data[:5])
        seq_ack_number, flags = header
        syn = bool(flags & 4)
        ack = bool(flags & 2)
        fin = bool(flags & 1)

        data = data[5:]

        return cls(seq_number=seq_ack_number, data=data, syn=syn, ack=ack, fin=fin)
