import os 

BUFFER_SIZE = 1024

# Server
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080
SERVER_FOLDER = os.getcwd() + os.sep + ".." + os.sep + "server_files" + os.sep


# Client 
CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 8081
CLIENT_FOLDER = os.getcwd() + os.sep + ".." + os.sep + "client_files" + os.sep



# Messages

MESSAGE_OK = str.encode("Ok")