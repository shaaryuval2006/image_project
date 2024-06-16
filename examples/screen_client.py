# scene_display_client.py

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import numpy as np
import pickle
import socket


class SceneDisplayClient:
    def __init__(self):
        self.scene = None
        self.display = (800, 600)  # You can set your desired display resolution here
        self.rotation_axis = np.array([0, 0, 1])
        self.fov = 120  # Initial FOV, you can change this if needed

        self.client_id = None
        self.server_ip = None
        self.server_port = None

        pygame.init()
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        self.init_graphic()

    def init_graphic(self):
        glMatrixMode(GL_PROJECTION)
        gluPerspective(self.fov, (self.display[0] / self.display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 0, 0, 0, 10, 0, 1, 0)  # Initial camera position

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                return True
        return False

    def draw_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.scene:
            glPushMatrix()
            glRotatef(self.scene.line_of_sight_angle, *self.rotation_axis)
            self.scene.draw()
            glPopMatrix()

        pygame.display.flip()

    def receive_scene(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("127.0.0.1", 8888))
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    msg_len = int(data[:10])
                    data = data[10:]
                    while len(data) < msg_len:
                        data += client_socket.recv(1024)
                    if self.client_id is None or self.server_ip is None or self.server_port is None:
                        client_id, server_ip, server_port = pickle.loads(data)
                        self.client_id = client_id
                        self.server_ip = server_ip
                        self.server_port = server_port
                    else:
                        self.scene = pickle.loads(data)
            except (ConnectionResetError, EOFError):
                print("Connection lost with the server.")
                break
        client_socket.close()

    def start_viewer(self):
        scene_thread = threading.Thread(target=self.receive_scene)
        scene_thread.start()

        while True:
            if self.handle_pygame_events():
                break
            self.draw_scene()
            pygame.time.wait(20)


if __name__ == "__main__":
    viewer = SceneDisplayClient()
    viewer.start_viewer()
