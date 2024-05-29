import socket
import threading
import time
import pickle
import scene
import protocol
# Cube positions for each client
cube_positions = [
    (-4.0, 3.0, -5.0),
    (-8.0, 0.0, -5.0),
    (-2.0, 0.0, -5.0)
]

clients = []

def handle_client(client_socket, address):
    print(f"Accepted connection from {address}")
    position = cube_positions.pop(0)  # Assign a position to the client
    proto = protocol.Protocol(client_socket)

    while True:

        try:
            scene_obj = scene.Scene()
            # Send cube position to the client
            data = pickle.dumps(scene_obj)
            msg = proto.create_msg("SCENE".encode() + protocol.Protocol.DELIMITER.encode() + data)
            client_socket.sendall(msg)
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

    #scene_thread = threading.Thread(target=handle_scene)
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
