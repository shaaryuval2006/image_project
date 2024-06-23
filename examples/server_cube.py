import socket
import threading
import pickle
import time
from master.scene import Scene

clients = []
texture_parts = [0.0, 1 / 3, 2 / 3, 1.0]
border_threshold = 35.0  # Adjust this threshold as needed
line_of_sight_angles = [0, 120, 240]
fov = 90


def handle_client(client_socket, address, part):
    print(f"Accepted connection from {address}")
    start = texture_parts[part]
    end = texture_parts[part + 1]
    texture_coords = [(start, 1), (start, 0), (end, 0), (end, 1)]

    line_of_sight_angle = line_of_sight_angles[part]
    scene = Scene(texture_coords, line_of_sight_angle, fov)

    x_offset = 0.0
    x_increment = 0.4  # Adjust the increment value as needed

    while True:
        try:
            # Update x_offset
            scene.update_x_offset(x_offset)
            x_offset += x_increment
            if x_offset > border_threshold:
                x_offset = 0.0
                part = (part + 1) % 3
                start = texture_parts[part]
                end = texture_parts[part + 1]
                texture_coords = [(start, 1), (start, 0), (end, 0), (end, 1)]
                rotation_angle = line_of_sight_angles[part]
                scene = Scene(texture_coords, rotation_angle, fov)  # Create a new scene for the next client

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
    server.bind(("0.0.0.0", 12345))
    server.listen(5)
    print("Server listening on port 12345   ")

    part = 0
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, part))
        client_thread.start()
        part = (part + 1) % 3  # Cycle through parts 0, 1, 2


if __name__ == "__main__":
    main()