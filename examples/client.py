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

def register():
    username = simpledialog.askstring("Register", "Enter your username:")
    password = simpledialog.askstring("Register", "Enter your password:", show='*')
    if username and password:
        network_handler.send_credentials(username, password, "1")
        response = network_handler.get_response()
        messagebox.showinfo("Response", response)

def sign_in():
    username = simpledialog.askstring("Sign In", "Enter your username:")
    password = simpledialog.askstring("Sign In", "Enter your password:", show='*')
    if username and password:
        network_handler.send_credentials(username, password, "2")
        response = network_handler.get_response()
        messagebox.showinfo("Response", response)

base = tk.Tk()
base.geometry('600x400')
button1 = tk.Button(base, text="Register", command=register, height=3, width=10, bg='lightblue')
button1.place(relx=0.3, rely=0.3)
button2 = tk.Button(base, text="Sign-in", command=sign_in, height=3, width=10, bg='lightgreen')
button2.place(relx=0.6, rely=0.3)

network_handler = NetworkHandler()
base.mainloop()
