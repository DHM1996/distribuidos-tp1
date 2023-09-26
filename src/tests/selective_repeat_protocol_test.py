import logging
import unittest
import threading

from src.lib.lossy_connection import LossyConnection
from src.lib.selective_repeat_protocol import SelectiveRepeatSender, SelectiveRepeatReceiver


class TestSelectiveRepeat(unittest.TestCase):
    def setUp(self):
        # Set up sender and receiver instances
        self.sender_connection = LossyConnection("localhost", 54321, timeout=1, loss_rate=0.0)
        self.receiver_connection = LossyConnection("localhost", 12345, timeout=1, loss_rate=0.0)
        self.sender = SelectiveRepeatSender(self.sender_connection, window_size=5, timeout=1)
        self.receiver = SelectiveRepeatReceiver(self.receiver_connection)

    def tearDown(self):
        # Clean up sender and receiver sockets
        self.sender_connection.close()
        self.receiver_connection.close()

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

        # Check if the received data matches sent data
        with open("received_file.txt", "rb") as received_file:
            received_data = received_file.read()
        self.assertEqual(received_data, test_data)


    def test_packet_loss(self):
        expected_length = 1000
        self.sender_connection.loss_rate = 0.5
        self.test_send_receive()
        with open("received_file.txt", "rb") as received_file:
                received_data = received_file.read()
                if (len(received_data) < expected_length):
                    logging.info(f"Packet loss detected. Expected length: {expected_length}, Received length: {len(received_data)}")

        self.sender.packet_loss_rate = 0.0

    def test_timeout(self):
        self.sender.timeout = 2
        self.test_send_receive()

    def test_window(self):
        self.sender.window_size = 3
        self.test_send_receive()



if __name__ == "__main__":
    unittest.main()