import pickle
import socket
import protocol

class NetworkHandler:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 9999))
        self.proto = protocol.Protocol(self.client_socket)

    def send_credentials(self, username, password, choice):
        obj = (username, password, choice)  # Add choice to the data to send
        data = pickle.dumps(obj)
        message = str(len(data)).zfill(10).encode() + data
        self.client_socket.sendall(message)

    def handle(self):
        print("1. Register")
        print("2. Sign in")
        choice = input("Enter your choice: ")
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        self.send_credentials(username, password, choice)
        while True:
            res, data = self.proto.get_msg()
            if res:
                msg = pickle.loads(data)
                print(msg)  # Print the received message from the server
                break
            else:
                print(data)
                break

def main():
    cview = NetworkHandler()
    cview.handle()

if __name__ == "__main__":
    main()
