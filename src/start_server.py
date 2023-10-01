import argparse
import logging

from conf.config import SERVER_IP, SERVER_PORT, SERVER_FOLDER
from lib.enums import Protocol
from lib.server import Server


def get_args():
    parser = argparse.ArgumentParser(description="Args", add_help=True)
    parser.add_argument(
        "-v", "--verbose", type=str, help="increase output verbosity", required=False
    )
    parser.add_argument(
        "-q", "--quiet", type=str, help="decrease output verbosity", required=False
    )
    parser.add_argument(
        "-H", "--host", type=str, help="service IP address", default=SERVER_IP, required=False
    )
    parser.add_argument(
        "-p", "--port", type=int, help="service port", default=SERVER_PORT, required=False
    )
    parser.add_argument(
        "-s", "--storage", type=str, help="storage dir path", default=SERVER_FOLDER, required=False
    )
    parser.add_argument(
        "-P", "--protocol", type=Protocol, help="protocol", default=Protocol.STOP_AND_WAIT, required=False
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)

    server = Server(args.host, args.port, args.protocol, args.storage)
    server.run()
