import socket
import threading
import pickle
import time
from scene import Scene
import sqlite3
import protocol


class Database:
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY,
                          username TEXT NOT NULL,
                          password TEXT NOT NULL)''')
        self.conn.commit()

    def add_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()

        print("Contents of the users table:")
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    def get_password(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", ((username),))
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
        self.protocol = protocol.Protocol(self.client_socket)

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
                res, data = self.protocol.get_msg()
                if data:
                    username, password, choice = pickle.loads(data)  # Unpack all values
                    db = Database()
                    if choice == "1":  # Register
                        existing_password = db.get_password(username)
                        if existing_password is None:
                            db.add_user(username, password)
                            print(f"Added new user: {username}")
                            response_msg = "User added successfully"
                        else:
                            print(f"Username '{username}' already exists")
                            response_msg = "Error: Username already exists"
                    elif choice == "2":  # Sign in
                        stored_password = db.get_password(username)
                        if stored_password == password:
                            response_msg = "Success: Logged in"
                        else:
                            response_msg = "Error: Incorrect password"
                    else:
                        response_msg = "Error: Invalid choice"
                    db.close()
                    print(response_msg)

                    response_data = pickle.dumps(response_msg)
                    data = self.protocol.create_msg(response_data)
                    self.client_socket.sendall(data)
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


'''"C:\Program Files\Python311\python.exe" C:\cyber\pyptojects\image_project8\examples\server_cube.py 
Server listening on port 9999
Accepted connection from ('127.0.0.1', 50365)
Exception in thread Thread-1:
Traceback (most recent call last):
  File "C:\Program Files\Python311\Lib\threading.py", line 1045, in _bootstrap_inner
    self.run()
  File "C:\cyber\pyptojects\image_project8\examples\server_cube.py", line 77, in run
    username, password = pickle.loads(data)
    ^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 2)'''