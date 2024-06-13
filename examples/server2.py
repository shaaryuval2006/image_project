import socket
import threading
import pickle
import sqlite3
import time
from scene import Scene
import protocol


clients = []
texture_parts = [0.0, 1 / 3, 2 / 3, 1.0]
border_threshold = 35.0  # Adjust this threshold as needed
line_of_sight_angles = [0, 120, 240]
fov = 90


class Database:
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_user_table()
        self.create_scene_table()

    def create_user_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY,
                          username TEXT NOT NULL,
                          password TEXT NOT NULL)''')
        self.conn.commit()

    def create_scene_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS scenes (
                          id INTEGER PRIMARY KEY,
                          username TEXT NOT NULL,
                          scene BLOB NOT NULL,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    def add_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

    def get_password(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def add_scene(self, username, scene):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO scenes (username, scene) VALUES (?, ?)", (username, scene))
        self.conn.commit()

    def get_scenes(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT scene, timestamp FROM scenes WHERE username=? ORDER BY timestamp DESC", (username,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()


class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.protocol = protocol.Protocol(self.client_socket)
        self.signed_in_clients = []

    def run(self):
        print(f"Accepted connection from {self.address}")
        while True:
            try:
                res, data = self.protocol.get_msg()
                if data:
                    username, password, choice = pickle.loads(data)
                    db = Database()
                    if choice == "register":  # Register
                        existing_password = db.get_password(username)
                        if existing_password is None:
                            db.add_user(username, password)
                            response_msg = "User added successfully"
                        else:
                            response_msg = "Error: Username already exists"
                    elif choice == "sign_in":  # Sign in
                        stored_password = db.get_password(username)
                        if stored_password == password:
                            response_msg = "Success: Logged in"
                        else:
                            response_msg = "Error: Incorrect password"
                    elif choice == "add_scene":  # Add scene
                        scene_data = pickle.loads(data[1])
                        db.add_scene(username, scene_data)
                        response_msg = "Scene added successfully"
                    elif choice == "get_scenes":  # Get scenes
                        scenes = db.get_scenes(username)
                        response_data = pickle.dumps(scenes)
                        data = self.protocol.create_msg(response_data)
                        self.client_socket.sendall(data)
                        continue
                    else:
                        response_msg = "Error: Invalid choice"
                    db.close()

                    response_data = pickle.dumps(response_msg)
                    data = self.protocol.create_msg(response_data)
                    self.client_socket.sendall(data)

                    if choice == "sign_in" and response_msg == "Success: Logged in":
                        res, data = self.protocol.get_msg()
                        if data:
                            num_screens = pickle.loads(data)
                            print(f"User {username} has {num_screens} screens")
                            self.signed_in_clients.append((self.client_socket, num_screens))
                            print(self.signed_in_clients)

            except (ConnectionResetError, BrokenPipeError):
                print(f"Connection lost with {self.address}")
                break
        self.client_socket.close()


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


def start_scene_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen(5)
    print("Scene server listening on port 12345")

    part = 0
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, part))
        client_thread.start()
        part = (part + 1) % 3  # Cycle through parts 0, 1, 2


def start_auth_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(5)
    print("Auth server listening on port 8888")

    while True:
        client_socket, addr = server.accept()
        client_handler = ClientHandler(client_socket, addr)
        client_handler.start()


if __name__ == "__main__":
    scene_server_thread = threading.Thread(target=start_scene_server)
    auth_server_thread = threading.Thread(target=start_auth_server)

    scene_server_thread.start()
    auth_server_thread.start()

    scene_server_thread.join()
    auth_server_thread.join()
