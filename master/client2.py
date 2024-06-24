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
        obj = (choice, username, password)
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def send_number_of_screens(self, username, num_screens, choice):
        obj = (choice, username, num_screens)
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def send_client_info(self, client_id, server_ip, server_port, ip_list):
        i = 0
        screen_clients_sockets = []
        for ip in ip_list:
            obj = (client_id, server_ip, server_port, i)
            i += 1
            data = pickle.dumps(obj)
            message = self.proto.create_msg(data)

            screen_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                screen_client_socket.connect((ip, 8889))
                screen_client_socket.sendall(message)
                screen_clients_sockets.append(screen_client_socket)
            except socket.error as e:
                print(f"Connection to {ip} failed: {e}")
        return screen_clients_sockets

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
        obj = ("add_scene", username, pickle.dumps(scene))
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def retrieve_scenes(self, username):
        obj = ("get_scenes", username)
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

        self.login_button = tk.Button(self.master, text="Sign_Up", command=self.sign_up, font=("helvetica", 16))
        self.login_button.place(relx=0.65, rely=0.70, anchor="center")

        self.sign_in_button = tk.Button(self.master, text="Sign In", command=self.sign_in, font=("helvetica", 16))
        self.sign_in_button.place(relx=0.35, rely=0.70, anchor="center")

        self.screen_clients_sockets = []

    def sign_up(self):
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
                    self.network_handler.send_number_of_screens(self.username, num_screens, "number_of_screens")
                    self.open_ip_input_window(num_screens)
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def open_ip_input_window(self, num_screens):
        ip_window = tk.Toplevel(self.master)
        ip_window.title("Enter IP Addresses")
        ip_window.geometry('400x400')

        ip_entries = []

        for i in range(num_screens):
            label = tk.Label(ip_window, text=f"Enter IP address for screen {i + 1}:", font=("helvetica", 12))
            label.pack(pady=5)
            entry = tk.Entry(ip_window, font=("helvetica", 12))
            entry.pack(pady=5)
            ip_entries.append(entry)

        submit_button = tk.Button(ip_window, text="Submit", command=lambda: self.submit_ips(ip_window, ip_entries), font=("helvetica", 12))
        submit_button.pack(pady=20)

    def submit_ips(self, ip_window, ip_entries):
        ip_list = [entry.get() for entry in ip_entries if entry.get()]

        # Check for duplicate IP addresses
        if len(ip_list) != len(set(ip_list)):
            messagebox.showerror("Error", "Duplicate IP addresses found. Please enter unique IP addresses.")
            return

        if len(ip_list) == len(ip_entries):
            client_id = self.username
            server_ip = "172.16.16.69"
            global server_port
            s_client_sockets = self.network_handler.send_client_info(client_id, server_ip, server_port, ip_list)
            self.screen_clients_sockets.extend(s_client_sockets)
            ip_window.destroy()
            self.master.withdraw()
        else:
            messagebox.showerror("Error", "Please enter all IP addresses.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI_Window(root)
    root.mainloop()
