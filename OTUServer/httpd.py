# stdlib
import argparse
import socket

# project
from request import Request


class Server:
    def __init__(self, address, port, max_connections=100):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.address = address
        self.port = port
        self.max_connections = max_connections

    def bind(self):
        self.server_sock.bind((self.address, self.port))
        self.server_sock.listen(self.max_connections)

    def run(self):
        while True:
            client_socket, client_address = self.server_sock.accept()

            data = self.receive_data(client_socket)
            if not data:
                continue

            response = Request(data, DOCUMENT_ROOT).get_response()
            print(data)

            print("отправка данных")
            client_socket.sendall(response)
            client_socket.close()

    @staticmethod
    def receive_data(sock) -> bytes:
        response = b""
        sock.settimeout(0.01)
        try:
            while True:
                chunk = sock.recv(4096)
                if len(chunk) == 0:  # No more data received, quitting
                    break
                response += chunk
        except TimeoutError as e:
            print(e)
        finally:
            sock.settimeout(None)
            return response


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--document_root", type=str, help="document root path: /OTUServer")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    ADDR = "0.0.0.0"
    PORT = 9000
    args = get_args()
    DOCUMENT_ROOT = args.document_root

    server = Server(ADDR, PORT)
    server.bind()
    server.run()
