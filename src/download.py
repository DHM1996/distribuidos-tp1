import argparse
import logging
import socket
from conf.config import CLIENT_FOLDER, BUFFER_SIZE

logging.basicConfig(level=logging.INFO)


class FileDownloaderClient:
    def __init__(self, buffer_size, client_folder):
        self.buffer_size = buffer_size
        self.client_folder = client_folder

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

            file_data = b""
            while True:
                file_chunk, _ = self.client_socket.recvfrom(self.buffer_size)
                if file_chunk.decode() == "UPLOAD_END" or not file_chunk:
                    break
                file_data += file_chunk

            with open(CLIENT_FOLDER + destination_path, "wb") as file:
                file.write(file_data)

            logging.info(
                f"Download file '{file_name}' was successful on '{destination_path}'"
            )

        except Exception as e:
            logging.error(f"Error while downloading: {str(e)}")
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
    downloader = FileDownloaderClient(BUFFER_SIZE, CLIENT_FOLDER)
    downloader.download_file(args.host, args.port, args.name, args.destination)
