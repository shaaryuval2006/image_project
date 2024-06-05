import socket
import threading
import pickle
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

    def get_password(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None

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
                            self.signed_in_clients.append(self.client_socket)

                        else:
                            response_msg = "Error: Incorrect password"
                    else:
                        response_msg = "Error: Invalid choice"
                    db.close()

                    response_data = pickle.dumps(response_msg)
                    data = self.protocol.create_msg(response_data)
                    self.client_socket.sendall(data)
            except (ConnectionResetError, BrokenPipeError):
                print(f"Connection lost with {self.address}")
                break
        self.client_socket.close()


class Server:
    def __init__(self, host="0.0.0.0", port=8888):
        self.host = host
        self.port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server listening on port {self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            client_handler = ClientHandler(client_socket, addr)
            client_handler.start()


if __name__ == "__main__":
    server = Server()
    server.start()
