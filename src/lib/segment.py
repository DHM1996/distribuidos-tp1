import struct


class Segment:
    def __init__(self, seq_ack_number, syn=False, ack=False, fin=False, data=b''):
        self.seq_ack_number = seq_ack_number
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

    def get_seq_ack_number(self):
        return self.seq_ack_number

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
        header = struct.pack('!IB', self.seq_ack_number, flags)
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

        return cls(seq_ack_number, syn, ack, fin, data)

    @classmethod
    def from_binary(cls, binary_data, max_length):
        """
        Split binary data into a list of Segment objects each with a defined maximum length.
        """
        segments = []

        for i, start_byte in enumerate(range(0, len(binary_data), max_length)):
            segment_data = binary_data[start_byte:start_byte + max_length]
            segment = cls(i, False, False, False, segment_data)
            segments.append(segment)

        if segments:
            segments[-1].FIN = True

        return segments

    @classmethod
    def to_binary(cls, segments):
        """
         Join a list of Segment objects back into binary data.
         """
        binary_data = b""

        for segment in segments:
            binary_data += segment.get_data()

        return binary_data
