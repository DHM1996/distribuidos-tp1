# distribuidos-tp1

INTRODUCCION A LOS SISTEMAS DISTRIBUIDOS - TP 1 


## Server

Para iniciar el servidor:
```sh
python3 src/start_server.py 
```

## Client - Download

Para descargar un archivo del servidor:
```sh
python download.py -H 127.0.0.1 -p 8080 -n prueba.txt -d descarga.txt
```