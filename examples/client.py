import pickle
import socket
import protocol

class NetworkHandler:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 9999))
        self.proto = protocol.Protocol(self.client_socket)

    def handle(self):
        while True:
            res, data = self.proto.get_msg()
            if res:
                msg = pickle.loads(data)

def main():
    cview = NetworkHandler()
    cview.handle()


if __name__ == "__main__":
    main()