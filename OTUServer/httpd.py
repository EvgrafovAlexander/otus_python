# stdlib
import argparse
import logging
import socket
import threading

# project
from request import Request


class Server:
    def __init__(
        self,
        address: str = "0.0.0.0",
        port: int = 9000,
        max_connections: int = 1000,
        document_root: str = "",
        workers: int = 1,
    ):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.address = address
        self.port = port
        self.max_connections = max_connections
        self.document_root = document_root
        self.workers = workers

    def bind(self):
        self.server_sock.bind((self.address, self.port))
        self.server_sock.listen(self.max_connections)
        logging.info(
            "Server bound at addr: %s, port: %s, max conn: %s", self.address, str(self.port), str(self.max_connections)
        )

    def run(self):
        while True:
            client_socket, client_address = self.server_sock.accept()
            thread = threading.Thread(
                target=self.request_handler,
                args=(
                    client_socket,
                    client_address,
                ),
            )
            thread.daemon = True
            thread.start()

    def request_handler(self, client_socket: socket.socket, client_address: tuple) -> None:
        data = self.receive_data(client_socket)
        if data:
            logging.info("Received message: %s", data)
            response = Request(data, self.document_root).get_response()
            client_socket.sendall(response)
            client_socket.close()

    @staticmethod
    def receive_data(sock: socket.socket) -> bytes:
        response = b""
        sock.settimeout(0.01)
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
        except TimeoutError:
            pass
        finally:
            sock.settimeout(None)
            return response


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-addr", "--address", type=str, help="server address: 0.0.0.0")
    parser.add_argument("-port", "--port", type=int, help="server port: 9000")
    parser.add_argument("-r", "--document_root", type=str, help="document root path: /OTUServer")
    parser.add_argument("-w", "--workers", type=int, help="workers: 4")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    document_root = args.document_root
    addr = args.address
    port = args.port
    workers = args.workers

    logging.basicConfig(
        format="[%(asctime)s] %(levelname).1s:%(message)s",
        level=logging.DEBUG,
        datefmt="%Y.%m.%d %H:%M:%S",
        filename=None,
    )

    server = Server(addr, port, document_root=document_root)
    server.bind()
    server.run()
