# stdlib
import socket

# project
from request import Request


class Server:
    def __init__(self, address, port, max_connections=5):
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

            response = Request(data).get_response()
            print(data)

            print("отправка данных")
            client_socket.sendall(response)
            client_socket.close()

    @staticmethod
    def receive_data(sock) -> bytes:
        response = b""
        sock.settimeout(1)
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


ADDR = "0.0.0.0"
PORT = 9000
server = Server(ADDR, PORT)
server.bind()
server.run()
