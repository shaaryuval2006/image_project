import tkinter as tk
from tkinter import simpledialog, messagebox
import pickle
import socket
import protocol


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
        self.master.geometry('600x400')

        self.button1 = tk.Button(self.master, text="Register", command=self.register, height=3, width=10,
                                 bg='lightblue')
        self.button1.place(relx=0.3, rely=0.3)

        self.button2 = tk.Button(self.master, text="Sign-in", command=self.sign_in, height=3, width=10, bg='lightgreen')
        self.button2.place(relx=0.6, rely=0.3)

    def register(self):
        username = simpledialog.askstring("Register", "Enter your username:")
        password = simpledialog.askstring("Register", "Enter your password:", show='*')
        if username and password:
            self.network_handler.send_credentials(username, password, "1")
            response = self.network_handler.get_response()
            messagebox.showinfo("Response", response)

    def sign_in(self):
        username = simpledialog.askstring("Sign In", "Enter your username:")
        password = simpledialog.askstring("Sign In", "Enter your password:", show='*')
        if username and password:
            self.network_handler.send_credentials(username, password, "2")
            response = self.network_handler.get_response()
            messagebox.showinfo("Response", response)


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI_Window(root)
    root.mainloop()
