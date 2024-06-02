import socket
import threading
import pickle
import time
from scene import Scene

clients = []
texture_parts = [0.0, 1 / 3, 2 / 3, 1.0]


def handle_client(client_socket, address, part):
    print(f"Accepted connection from {address}")
    # Calculate the texture coordinates based on the part
    start = texture_parts[part]
    end = texture_parts[part + 1]
    texture_coords = [(start, 1), (start, 0), (end, 0), (end, 1)]

    scene = Scene(texture_coords)

    while True:
        try:
            # Send scene to the client
            data = pickle.dumps(scene)
            message = str(len(data)).zfill(10).encode() + data
            client_socket.sendall(message)
            time.sleep(0.1)
        except (ConnectionResetError, BrokenPipeError):
            print(f"Connection lost with {address}")
            break

    client_socket.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 9999))
    server.listen(5)
    print("Server listening on port 9999")

    part = 0
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, part))
        client_thread.start()
        part = (part + 1) % 3  # Cycle through parts 0, 1, 2


if __name__ == "__main__":
    main()
