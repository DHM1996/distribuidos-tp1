import os
from typing import Union

from src.lib.connection import Connection
from src.lib.selective_repeat_protocol.selective_repeat_receiver import SelectiveRepeatReceiver
from src.lib.selective_repeat_protocol.selective_repeat_sender import SelectiveRepeatSender


class SelectiveRepeatProtocol:
    def __init__(self, connection: Connection, window_size=100):
        self.receiver = SelectiveRepeatReceiver(connection, window_size=window_size)
        self.sender = SelectiveRepeatSender(connection, window_size=window_size)

    def send_file(self, file_path: Union[str, os.PathLike], block=True):
        self.sender.send_file(file_path, block=block)

    def receive_file(self, file_path: Union[str, os.PathLike]):
        self.receiver.receive_file(file_path)
