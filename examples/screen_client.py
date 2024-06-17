# scene_display_client.py

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import numpy as np
import pickle
import socket
import protocol

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
        self.proto = protocol.Protocol(None)  # Initialize the protocol without a socket for now

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
        screen_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        screen_server_socket.bind(("127.0.0.1", 8889))
        screen_server_socket.listen(5)

        while True:
            client_socket, addr = screen_server_socket.accept()
            try:
                self.proto = protocol.Protocol(client_socket)
                data = client_socket.recv(1024)
                if data:
                    res, msg_len = self.proto.get_msg()
                    if res:
                        while len(data) < msg_len:
                            data += client_socket.recv(msg_len - len(data))
                        if self.client_id is None or self.server_ip is None or self.server_port is None:
                            client_info = pickle.loads(data)
                            self.client_id, self.server_ip, self.server_port = client_info
                            print(f"Client ID: {self.client_id}, Server IP: {self.server_ip}, Server Port: {self.server_port}")
                        else:
                            self.scene = pickle.loads(data)
                            print("Scene received and updated.")
            except (ConnectionResetError, EOFError) as e:
                print(f"Connection lost with the client: {e}")
                break
            client_socket.close()
        screen_server_socket.close()

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
