# distribuidos-tp1

INTRODUCCION A LOS SISTEMAS DISTRIBUIDOS - TP 1 

|integrantes|Padrón|
|----------------------|---------|
|Dario Markarian      |  98684|
|Facundo Nicolas Bravo   | 100151|
|Federico Rubachin       | 9608|
|Filyan Karagoz        | 101933
|Nicolas Bugliot         | 101694 |

## Server

Para iniciar el servidor:
```sh
python3 start_server.py -h

usage: start_server.py [-h] [-v VERBOSE] [-q QUIET] [-H HOST] [-p PORT] [-s STORAGE] [-P PROTOCOL]

Args

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSE, --verbose VERBOSE
                        increase output verbosity
  -q QUIET, --quiet QUIET
                        decrease output verbosity
  -H HOST, --host HOST  service IP address
  -p PORT, --port PORT  service port
  -s STORAGE, --storage STORAGE
                        storage dir path
  -P PROTOCOL, --protocol PROTOCOL
```


### Ejemplo de uso:
```sh
python3 start_server.py --protocol=SELECTIVE_REPEAT
```


## Client - Upload

Para subir un archivo al servidor:

```sh
python3 upload.py -h 

usage: upload.py [-h] [-v VERBOSE] [-q QUIET] [-H HOST] [-p PORT] [-s SRC] -f NAME [-P PROTOCOL]

Args

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSE, --verbose VERBOSE
                        increase output verbosity
  -q QUIET, --quiet QUIET
                        decrease output verbosity
  -H HOST, --host HOST  service IP address
  -p PORT, --port PORT  service port
  -s SRC, --src SRC     source file path
  -f NAME, --name NAME  file name
  -P PROTOCOL, --protocol PROTOCOL
                        protocol
```

### Ejemplo de uso:

```sh
python3 upload.py --name=imagen1.jpg --protocol=SELECTIVE_REPEAT
```

## Client - Download

Para descargar un archivo del servidor:

```sh
 python3 src/download.py -h 
usage: download.py [-h] [-v VERBOSE] [-q QUIET] [-H HOST] [-p PORT] [-d DST] -f NAME [-P PROTOCOL]

Args

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSE, --verbose VERBOSE
                        increase output verbosity
  -q QUIET, --quiet QUIET
                        decrease output verbosity
  -H HOST, --host HOST  service IP address
  -p PORT, --port PORT  service port
  -d DST, --dst DST     destination file path
  -f NAME, --name NAME  file name
  -P PROTOCOL, --protocol PROTOCOL
                        protocol
```

### Ejemplo:

```sh
python3 download.py --name=imagen2.jpg --protocol=SELECTIVE_REPEAT
```

# Comcast

## Descripción

Comcast es una herramienta de simulación de condiciones de red que te permite emular diferentes escenarios de conectividad de red en tu sistema. Puede ser especialmente útil para probar la resistencia y la capacidad de recuperación de tus aplicaciones en entornos de red variables.

## Uso básico

Para ejecutar Comcast con una pérdida de paquetes del 10% en el dispositivo de bucle local (`lo`), puedes utilizar el siguiente comando:

```bash
go run comcast.go --device=lo --packet-loss=10%
```

Esto simulará una red con una pérdida de paquetes del 10% en el dispositivo de bucle local.

## Detener el comcast
Para detener la simulación de Comcast, puedes utilizar el siguiente comando:


```bash
go run comcast.go --stop
```




