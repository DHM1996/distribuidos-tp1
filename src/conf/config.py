import os 

BUFFER_SIZE = 1024

MAX_CONNECTION_ATTEMPTS = 3
TIMEOUT = 1

# Server
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
SERVER_FOLDER = os.getcwd() + os.sep + ".." + os.sep + "server_folder" + os.sep


# Client 
CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 8081
CLIENT_FOLDER = os.getcwd() + os.sep + ".." + os.sep + "client_folder" + os.sep



# Messages

MESSAGE_OK = str.encode("Ok")