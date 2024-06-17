# main_client.py
import tkinter as tk
from tkinter import simpledialog, messagebox
import pickle
import socket
import protocol
import time

server_port = "0.0.0.0"

class NetworkHandler:
    def __init__(self, port):
        global server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("172.16.16.69", port))
        self.proto = protocol.Protocol(self.client_socket)
        self.scene = None
        server_port = port
        self.update = False

    def send_credentials(self, username, password, choice):
        obj = (username, password, choice)
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def send_number_of_screens(self, username, num_screens):
        obj = (username, num_screens)
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def send_client_info(self, client_id, server_ip, server_port):
        obj = (client_id, server_ip, server_port)
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)

        # Connect to the screen client
        screen_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        screen_client_socket.connect(("127.0.0.1", 8889))
        screen_client_socket.sendall(message)
        return screen_client_socket

    def get_response(self):
        while True:
            res, data = self.proto.get_msg()
            if res:
                try:
                    msg = pickle.loads(data)
                    return msg
                except pickle.UnpicklingError as e:
                    print(f"UnpicklingError: {e}")
                    return None
            else:
                return None

    def handle_scene(self):
        while True:
            if self.update:
                time.sleep(0.001)
            else:
                res, data = self.proto.get_msg()
                if res:
                    try:
                        self.scene = pickle.loads(data)
                        self.update = True
                    except pickle.UnpicklingError as e:
                        print(f"UnpicklingError in handle_scene: {e}")

    def store_scene(self, username, scene):
        obj = (username, "add_scene", pickle.dumps(scene))
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def retrieve_scenes(self, username):
        obj = (username, "get_scenes")
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)
        res, data = self.proto.get_msg()
        if res:
            try:
                scenes = pickle.loads(data)
                return scenes
            except pickle.UnpicklingError as e:
                print(f"UnpicklingError in retrieve_scenes: {e}")
                return None
        else:
            return None

class GUI_Window:
    def __init__(self, master):
        self.master = master
        self.network_handler = NetworkHandler(8888)
        self.master.title("Login Form")
        self.master.geometry('400x300')

        self.username = ""
        self.password = ""

        self.username_label = tk.Label(self.master, text="User Id:", font=("helvetica", 16))
        self.username_label.place(relx=0.5, rely=0.25, anchor="center")

        self.username_entry = tk.Entry(self.master, font=("helvetica", 16))
        self.username_entry.place(relx=0.5, rely=0.35, anchor="center")

        self.password_label = tk.Label(self.master, text="Password:", font=("helvetica", 16))
        self.password_label.place(relx=0.5, rely=0.45, anchor="center")

        self.password_entry = tk.Entry(self.master, show="*", font=("helvetica", 16))
        self.password_entry.place(relx=0.5, rely=0.55, anchor="center")

        self.login_button = tk.Button(self.master, text="Sign_Up", command=self.login, font=("helvetica", 16))
        self.login_button.place(relx=0.65, rely=0.70, anchor="center")

        self.sign_in_button = tk.Button(self.master, text="Sign In", command=self.sign_in, font=("helvetica", 16))
        self.sign_in_button.place(relx=0.35, rely=0.70, anchor="center")

        self.screen_clients_sockets = []

    def login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        if self.username and self.password:
            self.network_handler.send_credentials(self.username, self.password, "sign_in")
            response = self.network_handler.get_response()
            if "Success" in response:
                messagebox.showinfo("Login", "this username is taken, {}".format(self.username))
            else:
                self.network_handler.send_credentials(self.username, self.password, "register")
                response = self.network_handler.get_response()
                messagebox.showinfo("Registration", response)
            self.master.withdraw()  # Hide the GUI window
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def sign_in(self):
        global server_port
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        if self.username and self.password:
            self.network_handler.send_credentials(self.username, self.password, "sign_in")
            response = self.network_handler.get_response()
            messagebox.showinfo("Response", response)
            if "Success" in response:
                num_screens = simpledialog.askinteger("Number of Screens", "Enter the number of screens:")

                if num_screens is not None:
                    self.network_handler.send_number_of_screens(self.username, num_screens)
                    client_id = self.password
                    server_ip = "172.16.16.69"
                    server_port = server_port
                    s_client_sock = self.network_handler.send_client_info(client_id, server_ip, server_port)
                    self.screen_clients_sockets.append(s_client_sock)
                    self.master.withdraw()
        else:
            messagebox.showerror("Error", "Please enter both username and password.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI_Window(root)
    root.mainloop()
