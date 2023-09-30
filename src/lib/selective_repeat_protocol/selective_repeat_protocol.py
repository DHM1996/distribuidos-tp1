from lib.selective_repeat_protocol.selective_repeat_receiver import SelectiveRepeatReceiver
from lib.selective_repeat_protocol.selective_repeat_sender import SelectiveRepeatSender


class SelectiveRepeatProtocol:
    def __init__(self, socket, server_host, server_port, recv_queue=None):
        self.receiver = SelectiveRepeatReceiver(socket, server_host, server_port, recv_queue=recv_queue, window_size=100)
        self.sender = SelectiveRepeatSender(socket, server_host, server_port, recv_queue=recv_queue, window_size=100)

    def send_file(self, file_path):
        self.sender.send_file(file_path)

    def receive_file(self, file_path):
        self.receiver.receive_file(file_path)
