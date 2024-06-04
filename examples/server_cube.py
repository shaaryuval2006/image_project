import socket
import threading
import pickle
import time
from scene import Scene
import sqlite3


class Database:
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        pass

    def add_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute(username, password)
        self.conn.commit()

    def get_password(self, username):
        cursor = self.conn.cursor()
        cursor.execute(username,)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def close(self):
        self.conn.close()


class ClientHandler(threading.Thread):
    texture_parts = [0.0, 1 / 3, 2 / 3, 1.0]
    border_threshold = 35.0
    line_of_sight_angles = [0, 120, 240]
    fov = 90

    def __init__(self, client_socket, address, part):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.part = part
        self.x_offset = 0.0
        self.x_increment = 0.4
        self.setup_scene()

    def setup_scene(self):
        start = self.texture_parts[self.part]
        end = self.texture_parts[self.part + 1]
        texture_coords = [(start, 1), (start, 0), (end, 0), (end, 1)]
        line_of_sight_angle = self.line_of_sight_angles[self.part]
        self.scene = Scene(texture_coords, line_of_sight_angle, self.fov)

    def run(self):
        print(f"Accepted connection from {self.address}")
        while True:
            try:
                self.update_scene()
                data = pickle.dumps(self.scene)
                message = str(len(data)).zfill(10).encode() + data
                self.client_socket.sendall(message)
                time.sleep(0.1)
            except (ConnectionResetError, BrokenPipeError):
                print(f"Connection lost with {self.address}")
                break
        self.client_socket.close()

    def update_scene(self):
        self.scene.update_x_offset(self.x_offset)
        self.x_offset += self.x_increment
        if self.x_offset > self.border_threshold:
            self.x_offset = 0.0
            self.part = (self.part + 1) % 3
            self.setup_scene()


class Server:
    def __init__(self, host="0.0.0.0", port=9999):
        self.host = host
        self.port = port
        self.clients = []
        self.part = 0

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server listening on port {self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            self.clients.append(client_socket)
            client_handler = ClientHandler(client_socket, addr, self.part)
            client_handler.start()
            self.part = (self.part + 1) % 3


if __name__ == "__main__":
    server = Server()
    server.start()
