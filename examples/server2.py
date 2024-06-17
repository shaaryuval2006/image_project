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

    def get_scenes(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT scene, timestamp FROM scenes WHERE username=? ORDER BY timestamp DESC", (username,))
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
                    message = pickle.loads(data)
                    # user client
                    if isinstance(message, tuple) and len(message) == 3:
                        username, password, choice = message
                        db = Database()
                        if choice == "register":  # Register
                            existing_password = db.get_password(username)
                            if existing_password is None:
                                db.add_user(username, password)
                                user_id = db.get_user_id(username)
                                default_scene = pickle.dumps(Scene())
                                db.add_scene(user_id, default_scene)
                                response_msg = "User added successfully".encode()
                            else:
                                response_msg = "Error: Username already exists".encode()
                        elif choice == "sign_in":  # Sign in
                            stored_password = db.get_password(username)
                            if stored_password == password:
                                user_id = db.get_user_id(username)
                                id = user_id
                                response_msg = "Success: Logged in".encode()
                            else:
                                response_msg = "Error: Incorrect password".encode()
                        elif choice == "add_scene":  # Add scene
                            response_msg = "Scene added successfully".encode()
                        elif choice == "get_scenes":  # Get scenes
                            scenes = db.get_scenes(username)
                            response_msg = scenes
                            #response_msg = self.protocol.create_msg(response_data)
                            #self.client_socket.sendall(data)
                            #continue
                        elif choice == "num_of_screens":
                            num_screens = pickle.loads(data)
                            print(f"User {username} has {num_screens} screens")
                            self.signed_in_users.append((username, id, num_screens))
                            print(self.signed_in_users)
                        else:
                            response_msg = "Error: Invalid choice".encode()
                        db.close()

                        #response_data = pickle.dumps(response_msg)
                        data = self.protocol.create_msg(response_msg)
                        self.client_socket.sendall(data)


                                # # Calculate FOV based on the number of screens
                                # fov = 360 / num_screens
                                #
                                # # Send scene with the updated FOV
                                # for part in range(num_screens):
                                #     start = texture_parts[part]
                                #     end = texture_parts[part + 1]
                                #     texture_coords = [(start, 1), (start, 0), (end, 0), (end, 1)]
                                #     line_of_sight_angle = line_of_sight_angles[part]
                                #     scene = Scene(texture_coords, line_of_sight_angle, fov)
                                #
                                #     data = pickle.dumps(scene)
                                #     message = self.protocol.create_msg(data)
                                #     self.client_socket.sendall(message)

                    else: # screen client
                        if choice == "client_id":
                            client_id = pickle.loads(data)
                        for user_details in self.signed_in_users:
                            print(user_details)
                            if user_details[0] == client_id:
                                print(f"Sending scene to screen client with ID: {client_id}")
                                try:
                                    message = self.protocol.create_msg(data)
                                    self.client_socket.sendall(message)
                                except Exception as e:
                                    print(f"Failed to send scene to screen client: {e}")
                            else:
                                self.client_socket.sendall("Don't Know You!".encode())
                                self.client_socket.close()
                                return # we want to disconnect from this client imitating to be a sceen client
                        print(f"Received an unknown message format. : {client_id}")
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
