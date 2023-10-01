from src.lib.selective_repeat_protocol.selective_repeat_receiver import SelectiveRepeatReceiver
from src.lib.selective_repeat_protocol.selective_repeat_sender import SelectiveRepeatSender


def test_without_loss_little_text(connections, tmp_path, helpers):
    little_text = "HELLO WORLD! WHAT A NICE DAY! WE ARE HERE TESTING THE SELECTIVE REPEAT PROTOCOL!"
    file_path = tmp_path / "little_text.txt"

    helpers.string_to_file(little_text, file_path)

    sender = SelectiveRepeatSender(connections["sender_connection"], window_size=20)

    receiver = SelectiveRepeatReceiver(connections["receiver_connection"], window_size=20)

    sender.send_file(file_path, block=False)

    received_file_path = tmp_path / "received_little_text.txt"
    receiver.receive_file(received_file_path)

    received_little_text = helpers.file_to_string(received_file_path)

    sender.wait_threads()

    assert little_text == received_little_text

def test_without_loss_small_file_small_window(connections, random_25kb_file, tmp_path, helpers):

    hash_original = helpers.hash_file(random_25kb_file)

    window_size = 3
    sender = SelectiveRepeatSender(connections["sender_connection"], window_size=window_size, timeout=1)
    receiver = SelectiveRepeatReceiver(connections["receiver_connection"], window_size=window_size)

    sender.send_file(random_25kb_file, block=False)

    received_file_path = tmp_path / "received_file.txt"
    receiver.receive_file(received_file_path)

    sender.wait_threads()

    hash_transmitted = helpers.hash_file(received_file_path)

    assert hash_original == hash_transmitted


def test_with_loss_small_file_small_window(connections, random_25kb_file, tmp_path, helpers):

    hash_original = helpers.hash_file(random_25kb_file)

    connections["sender_connection"].set_loss_rate(0.05)

    window_size = 3
    sender = SelectiveRepeatSender(connections["sender_connection"], window_size=window_size, timeout=1)
    receiver = SelectiveRepeatReceiver(connections["receiver_connection"], window_size=window_size)

    sender.send_file(random_25kb_file, block=False)

    received_file_path = tmp_path / "received_file.txt"
    receiver.receive_file(received_file_path)

    sender.wait_threads()

    hash_transmitted = helpers.hash_file(received_file_path)

    assert hash_original == hash_transmitted

def test_with_loss_small_file_big_window(connections, random_25kb_file, tmp_path, helpers):

    hash_original = helpers.hash_file(random_25kb_file)

    connections["sender_connection"].set_loss_rate(0.05)

    window_size = 300
    sender = SelectiveRepeatSender(connections["sender_connection"], window_size=window_size, timeout=1)
    receiver = SelectiveRepeatReceiver(connections["receiver_connection"], window_size=window_size)

    sender.send_file(random_25kb_file, block=False)

    received_file_path = tmp_path / "received_file.txt"
    receiver.receive_file(received_file_path)

    sender.wait_threads()

    hash_transmitted = helpers.hash_file(received_file_path)

    assert hash_original == hash_transmitted


def test_with_loss_big_file(connections, random_5mb_file, tmp_path, helpers):

    hash_original = helpers.hash_file(random_5mb_file)

    connections["sender_connection"].set_loss_rate(0.05)

    window_size = 50
    sender = SelectiveRepeatSender(connections["sender_connection"], window_size=window_size, timeout=1)
    receiver = SelectiveRepeatReceiver(connections["receiver_connection"], window_size=window_size)

    sender.send_file(random_5mb_file, block=False)

    received_file_path = tmp_path / "received_file.txt"
    receiver.receive_file(received_file_path)

    sender.wait_threads()

    hash_transmitted = helpers.hash_file(received_file_path)

    assert hash_original == hash_transmitted
