import tkinter as tk
from tkinter import simpledialog, messagebox
import pickle
import socket
import protocol
import time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import numpy as np
from scene import Scene


class NetworkHandler:
    def __init__(self, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", port))
        self.proto = protocol.Protocol(self.client_socket)
        self.scene = None
        self.update = False

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

    def handle_scene(self):
        while True:
            if self.update:
                time.sleep(0.001)
            else:
                res, data = self.proto.get_msg()
                if res:
                    self.scene = pickle.loads(data)
                    self.update = True

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
            scenes = pickle.loads(data)
            return scenes
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
        else:
            messagebox.showerror("Error", "Please enter both username and password.")

    def sign_in(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        if self.username and self.password:
            self.network_handler.send_credentials(self.username, self.password, "sign_in")
            response = self.network_handler.get_response()
            messagebox.showinfo("Response", response)
            if "Success" in response:
                num_screens = simpledialog.askinteger("Number of Screens", "Enter the number of screens:")
                if num_screens is not None:
                    self.network_handler.send_number_of_screens(num_screens)
                    self.master.destroy()  # Close the login window and start the scene viewer
                    SceneViewer(num_screens).start_viewer()
        else:
            messagebox.showerror("Error", "Please enter both username and password.")


class SceneViewer:
    def __init__(self, num_screens):
        self.network = NetworkHandler(12345)
        self.rotation_axis = np.array([0, 0, 1])

        pygame.init()
        info = pygame.display.Info()
        self.display = (info.current_w, info.current_h)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL | FULLSCREEN)
        self.scale_factor = 0.5

        self.eye = np.array([0, 0, 0])
        self.center = np.array([0, 0, 10])
        self.up = np.array([0, 1, 0])

        self.line_of_sight_angle = 0
        self.num_screens = num_screens
        self.fov = 360 / num_screens
        self.rotation_axis = np.array([0, 1, 0])

        self.scene = None
        self.fov_update = False

    def init_graphic(self):
        glMatrixMode(GL_PROJECTION)
        gluPerspective(self.fov, (self.display[0] / self.display[1]), 0.1, 50.0)  # Set initial FOV here
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(self.eye[0], self.eye[1], self.eye[2], self.center[0], self.center[1], self.center[2], self.up[0],
                  self.up[1], self.up[2])

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True, "EXIT"
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                return True, "EXIT"
        return False, None

    def iteration(self):
        res, cmd = self.handle_pygame_events()
        if res:
            return cmd

        if self.network.update:
            if self.fov != self.network.scene.fov:
                self.fov = self.network.scene.fov
                self.fov_update = True
            self.scene = self.network.scene
            self.network.update = False

        self.draw_scene()

    def draw_scene(self):
        if self.fov_update:
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(self.fov, (self.display[0] / self.display[1]), 0.1, 50.0)
            glMatrixMode(GL_MODELVIEW)
            self.fov_update = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.scene:
            if self.scene.line_of_sight_angle is not None:
                self.line_of_sight_angle = self.scene.line_of_sight_angle

            cur_eye, cur_center = rotate_vector(self.eye, self.center, self.line_of_sight_angle, self.rotation_axis)
            gluLookAt(cur_eye[0], cur_eye[1], cur_eye[2], cur_center[0], cur_center[1], cur_center[2], self.up[0],
                      self.up[1], self.up[2])

            self.scene.draw()
            print("FOV:", self.scene.fov)
            pygame.display.flip()

    def start_viewer(self):
        thread = threading.Thread(target=self.network.handle_scene)
        thread.start()
        self.init_graphic()

        while True:
            cmd = self.iteration()
            if cmd == "EXIT":
                break
            pygame.time.wait(20)


def rotate_vector(eye, center, angle_degrees, axis):
    vector = center - eye
    angle_radians = np.radians(angle_degrees)
    cos_theta = np.cos(angle_radians)
    sin_theta = np.sin(angle_radians)
    u = np.array(axis)
    u = u / np.linalg.norm(u)

    rotation_matrix = np.array([
        [
            cos_theta + u[0] * u[0] * (1 - cos_theta),
            u[0] * u[1] * (1 - cos_theta) - u[2] * sin_theta,
            u[0] * u[2] * (1 - cos_theta) + u[1] * sin_theta
        ],
        [
            u[1] * u[0] * (1 - cos_theta) + u[2] * sin_theta,
            cos_theta + u[1] * u[1] * (1 - cos_theta),
            u[1] * u[2] * (1 - cos_theta) - u[0] * sin_theta
        ],
        [
            u[2] * u[0] * (1 - cos_theta) - u[1] * sin_theta,
            u[2] * u[1] * (1 - cos_theta) + u[0] * sin_theta,
            cos_theta + u[2] * u[2] * (1 - cos_theta)
        ]
    ])

    dir_vector = np.dot(rotation_matrix, vector)
    return eye, eye + dir_vector


if __name__ == "__main__":
    root = tk.Tk()
    app = GUI_Window(root)
    root.mainloop()
