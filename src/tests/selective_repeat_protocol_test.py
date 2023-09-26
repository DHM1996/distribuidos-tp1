from src.lib.selective_repeat_protocol import SelectiveRepeatSender, SelectiveRepeatReceiver

def test_without_loss(sender_connection, receiver_connection, random_5mb_file, helpers, tmp_path):

    hash_original = helpers.hash_file(random_5mb_file)

    sender = SelectiveRepeatSender(sender_connection, window_size=20, timeout=1)

    receiver = SelectiveRepeatReceiver(receiver_connection, window_size=20)

    sender.send_file(random_5mb_file, block=False)

    received_file_path = tmp_path / "received_file.txt"
    receiver.receive_file(received_file_path)

    hash_transmitted = helpers.hash_file(received_file_path)

    assert hash_original == hash_transmitted
