# server_cube.py

import socket
import threading
import pickle
import time
from scene import Scene

cube_positions = [
    -2, 2

]

clients = []

def handle_client(client_socket, address):
    print(f"Accepted connection from {address}")
    #positions = [cube_positions.pop(0)]  # Assign positions to the client
    scene = Scene(cube_positions)

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

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
