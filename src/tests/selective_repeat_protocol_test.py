import unittest
import socket
import threading
import time

from src.lib.selective_repeat_protocol import SelectiveRepeatSender, SelectiveRepeatReceiver


class TestSelectiveRepeat(unittest.TestCase):
    def setUp(self):
        # Set up sender and receiver instances
        self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sender_address = ("localhost", 12345)
        self.receiver_address = ("localhost", 54321)
        self.sender = SelectiveRepeatSender(self.sender_socket, self.receiver_address, window_size=5)
        self.receiver = SelectiveRepeatReceiver(self.receiver_socket, self.receiver_address)

    def tearDown(self):
        # Clean up sender and receiver sockets
        self.sender_socket.close()
        self.receiver_socket.close()

    def test_send_receive(self):
        # Create a file with test data
        test_data = b"Hello, Selective Repeat!"
        with open("test_file.txt", "wb") as test_file:
            test_file.write(test_data)

        # Start receiver in a separate thread
        receiver_thread = threading.Thread(target=self.receiver.receive)
        receiver_thread.start()

        # Send the file using the sender
        self.sender.send_file("test_file.txt")

        # Wait for the receiver to finish
        receiver_thread.join()

        # Check if the received data matches the sent data
        with open("received_file.txt", "rb") as received_file:
            received_data = received_file.read()
        self.assertEqual(received_data, test_data)


    self test_packet_loss(self):
        expected_length = 1000
        self.sender.packet_loss_rate = 0.5
        test_send_receive(self)
        with open("received_file.txt", "rb") as received_file:
                received_data = received_file.read()
                if (len(received_data) < expected_length):
                    logging.info(f"Packet loss detected. Expected length: {expected_length}, Received length: {len(received_data)}")

        self.sender.packet_loss_rate = 0.0

    def test_timeout(self):
        self.sender.timeout = 2
        self.test_send_receive(self)

    def test_window(self):
        self.sender.window_size = 3
        self.test_send_receive(self)



if __name__ == "__main__":
    unittest.main()