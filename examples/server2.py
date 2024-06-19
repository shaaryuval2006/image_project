import socket
import threading
import pickle
import sqlite3
import protocol
from scene import Scene

texture_parts = [0.0, 1 / 3, 2 / 3, 1.0]
border_threshold = 35.0  # Adjust this threshold as needed
line_of_sight_angles = [0, 120, 240]
id = 0

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
                          user_id INTEGER NOT NULL,
                          scene BLOB NOT NULL,
                          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY(user_id) REFERENCES users(id))''')
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

    def get_user_id(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def add_scene(self, user_id, scene_data):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO scenes (user_id, scene) VALUES (?, ?)", (user_id, scene_data))
        self.conn.commit()

    def get_latest_scene(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT scene FROM scenes WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_scenes(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT scene, timestamp FROM scenes WHERE user_id=(SELECT id FROM users WHERE username=?) ORDER BY timestamp DESC", (username,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address, signed_in_users):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.protocol = protocol.Protocol(self.client_socket)
        self.signed_in_users = signed_in_users

    def run(self):
        global id
        print(f"Accepted connection from {self.address}")
        while True:
            try:
                res, data = self.protocol.get_msg()
                if res:
                    try:
                        message = pickle.loads(data)
                    except pickle.UnpicklingError as e:
                        print(f"UnpicklingError: {e}")
                        continue

                    #main client
                    print(message, "this is the message")
                    if not isinstance(message, tuple):
                        print(f"Received an unknown message format: {message}")
                        self.client_socket.sendall(b"Invalid username")
                        self.client_socket.close()
                        return

                    print(f"message len = {len(message)}")
                    if len(message) == 3:
                        username, password, choice = message
                        db = Database()
                        if choice == "register":  # Register
                            existing_password = db.get_password(username)
                            if existing_password is None:
                                db.add_user(username, password)
                                user_id = db.get_user_id(username)
                                default_scene = pickle.dumps(Scene())
                                db.add_scene(user_id, default_scene)
                                response_msg = "User added successfully"
                            else:
                                response_msg = "Error: Username already exists"
                        elif choice == "sign_in":  # Sign in
                            stored_password = db.get_password(username)
                            if stored_password == password:
                                user_id = db.get_user_id(username)
                                id = user_id
                                response_msg = "Success: Logged in"
                            else:
                                response_msg = "Error: Incorrect password"
                        elif choice == "add_scene":  # Add scene
                            response_msg = "Scene added successfully"
                        elif choice == "get_scenes":  # Get scenes
                            scenes = db.get_scenes(username)
                            response_msg = scenes
                        elif choice == "number_of_screens":
                            num_screens = pickle.loads(data)
                            print(f"User {username} has {num_screens} screens")
                            self.signed_in_users.append((username, id, num_screens))
                            continue
                        else:
                            response_msg = "Error: Invalid choice"
                        db.close()

                        data = pickle.dumps(response_msg)
                        message = self.protocol.create_msg(data)
                        self.client_socket.sendall(message)

                    #screen client
                    elif len(message) == 2:
                        cmd, data = message

                        if cmd == "screen_connect":
                            db = Database()
                            client_id = data

                            print("yuval", self.signed_in_users)
                            for user_details in self.signed_in_users:
                                print(f"user details {user_details}, client_id {client_id}")
                                if user_details[0] == client_id:
                                    try:
                                        user_id = user_details[1]
                                        scene_data = db.get_latest_scene(user_id)
                                        print("eli")
                                        message = self.protocol.create_msg(pickle.dumps(("scene", scene_data)))
                                        self.client_socket.sendall(message)
                                    except Exception as e:
                                        print(f"Failed to send scene to screen client: {e}")
                                else:
                                    self.client_socket.sendall(b"Don't Know You")
                                    self.client_socket.close()
                                    return
                            print(f"Received a message for username: {client_id}")

                            db.close()
                    else:
                        print(message)
            except (ConnectionResetError, BrokenPipeError):
                print(f"Connection lost with {self.address}")
                break
        self.client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(5)
    print("Server listening on port 8888")
    assigned_clients = []
    while True:
        client_socket, addr = server.accept()
        client_handler = ClientHandler(client_socket, addr, assigned_clients)
        client_handler.start()


if __name__ == "__main__":
    start_server()
