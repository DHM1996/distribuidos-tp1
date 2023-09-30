import argparse
import logging
import socket
from conf.config import BUFFER_SIZE
from lib.stop_and_wait_protocol import StopAndWaitProtocol


class FileDownloaderClient:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.client_socket = None

    def create_socket(self):
        self.client_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )
        logging.info("Socket created")

    def close_socket(self):
        self.client_socket.close()

    def send_download_command(self, file_name, server_ip, server_port):
        command = f"DOWNLOAD_START {file_name}"
        self.client_socket.sendto(command.encode(), (server_ip, server_port))
        logging.info(f"Downloading file '{file_name}'")

    def download_file(self, server_ip, server_port, file_name, destination_path):
        self.create_socket()
        try:
            self.send_download_command(file_name, server_ip, server_port)
            protocol = StopAndWaitProtocol(self.client_socket, (server_ip, server_port))
            protocol.receive_file(destination_path)

            logging.info(
                f"Download file '{file_name}' was successful on '{destination_path}'"
            )

        #except Exception as e:
        #    logging.error(f"Error while downloading: {str(e)}")
        finally:
            self.close_socket()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente de descarga de archivos")
    parser.add_argument(
        "-H", "--host", type=str, help="Dirección IP del servidor", required=True
    )
    parser.add_argument(
        "-p", "--port", type=int, help="Puerto del servidor", required=True
    )
    parser.add_argument(
        "-n", "--name", type=str, help="Nombre del archivo a descargar", required=True
    )
    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        help="Ruta de destino para guardar el archivo",
        required=True,
    )

    args = parser.parse_args()
    downloader = FileDownloaderClient(BUFFER_SIZE)
    downloader.download_file(args.host, args.port, args.name, args.destination)
