import argparse
import logging
import os

from upload import create_socket, close_socket

BUFFER_SIZE = 1024

CLIENT_FOLDER = os.getcwd() + os.sep + ".." + os.sep + "client_files" + os.sep


def send_download_command(client_socket, file_name, server_ip, server_port):
    command = f"DOWNLOAD_START {file_name}"
    client_socket.sendto(command.encode(), (server_ip, server_port))
    logging.info(f"Downloading file '{file_name}'")


def download_file(server_ip, server_port, file_name, destination_path):
    client_socket = create_socket()
    try:
        send_download_command(client_socket, file_name, server_ip, server_port)

        file_data = b""
        while True:
            file_chunk, _ = client_socket.recvfrom(BUFFER_SIZE)
            if file_chunk.decode() == "UPLOAD_END" or not file_chunk:
                break
            file_data += file_chunk

        with open(CLIENT_FOLDER + destination_path, 'wb') as file:
            file.write(file_data)

        logging.info(f"Download file '{file_name}' was successful on '{destination_path}'")

    except Exception as e:
        logging.error(f"Error while downloading: {str(e)}")
    finally:
        close_socket(client_socket)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente de descarga de archivos")
    parser.add_argument("-H", "--host", type=str, help="Dirección IP del servidor", required=True)
    parser.add_argument("-p", "--port", type=int, help="Puerto del servidor", required=True)
    parser.add_argument("-n", "--name", type=str, help="Nombre del archivo a descargar", required=True)
    parser.add_argument("-d", "--destination", type=str, help="Ruta de destino para guardar el archivo", required=True)

    args = parser.parse_args()
    download_file(args.host, args.port, args.name, args.destination)
