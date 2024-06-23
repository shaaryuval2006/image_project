import tkinter as tk
from tkinter import simpledialog, messagebox
import pickle
import socket
from master import protocol


class NetworkHandler:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 8888))
        self.proto = protocol.Protocol(self.client_socket)

    def send_credentials(self, username, password, choice):
        obj = (username, password, choice)
        data = pickle.dumps(obj)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def send_number_of_screens(self, num_screens):
        data = pickle.dumps(num_screens)
        message = self.proto.create_msg(data)
        self.client_socket.sendall(message)

    def get_response(self):
        while True:
            res, data = self.proto.get_msg()
            if res:
                msg = pickle.loads(data)
                return msg
            else:
                return data


class GUI_Window:
    def __init__(self, master):
        self.master = master
        self.network_handler = NetworkHandler()
        self.master.title("Login Form")
        self.master.geometry('600x400')

        # Initialize username and password variables
        self.username = ""
        self.password = ""

        self.username_label = tk.Label(self.master, text="Userid:")
        self.username_label.place(relx=0.5, rely=0.35, anchor="center")

        self.username_entry = tk.Entry(self.master)
        self.username_entry.place(relx=0.5, rely=0.40, anchor="center")

        self.password_label = tk.Label(self.master, text="Password:")
        self.password_label.place(relx=0.5, rely=0.45, anchor="center")

        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.place(relx=0.5, rely=0.5, anchor="center")

        self.login_button = tk.Button(self.master, text="Login", command=self.login)
        self.login_button.place(relx=0.55, rely=0.6, anchor="center")

        self.sign_in_button = tk.Button(self.master, text="Sign In", command=self.sign_in)
        self.sign_in_button.place(relx=0.45, rely=0.6, anchor="center")

    def login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        # Check if username and password are not empty
        if self.username and self.password:
            # First, attempt to sign in
            self.network_handler.send_credentials(self.username, self.password, "sign_in")
            response = self.network_handler.get_response()
            if "Success" in response:
                messagebox.showinfo("Login", "Welcome back, {}".format(self.username))
            else:
                # If sign-in fails, attempt to register
                self.network_handler.send_credentials(self.username, self.password, "register")
                response = self.network_handler.get_response()
                messagebox.showinfo("Registration", response)
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def sign_in(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        # Check if username and password are not empty
        if self.username and self.password:
            self.network_handler.send_credentials(self.username, self.password, "sign_in")
            response = self.network_handler.get_response()
            messagebox.showinfo("Response", response)
            if "Success" in response:
                num_screens = simpledialog.askinteger("Number of Screens", "Enter the number of screens:")
                if num_screens is not None:
                    self.network_handler.send_number_of_screens(num_screens)
        else:
            messagebox.showerror("Error", "Please enter both username and password.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI_Window(root)
    root.mainloop()
