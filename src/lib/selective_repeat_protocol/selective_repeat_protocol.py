from src.lib.selective_repeat_protocol import SelectiveRepeatReceiver, SelectiveRepeatSender


class SelectiveRepeatProtocol:

    def __int__(self, socket, server_host, server_port, recv_queue=None):

        self.receiver = SelectiveRepeatReceiver(socket, server_host, server_port, recv_queue=recv_queue)
        self.sender = SelectiveRepeatSender(socket, server_host, server_port, recv_queue=recv_queue)

    def send_file(self, file_path):
        self.sender.send_file(file_path)

    def receive_file(self, file_path):
        self.receiver.receive_file(file_path)
