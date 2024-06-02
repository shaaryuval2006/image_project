# client_cube.py

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import socket
import pickle
import threading
import protocol
from scene import Scene
import numpy as np


def rotate_vector(vector, angle_degrees, axis):
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

    return np.dot(rotation_matrix, vector)


class NetworkHandler:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 9999))
        self.proto = protocol.Protocol(self.client_socket)
        self.scene = None
        self.update = False

    def handle(self):
        while True:
            res, data = self.proto.get_msg()
            if res:
                self.scene = pickle.loads(data)
                self.update = True


class ClientViewer:
    EXIT = 0

    def __init__(self):
        # Network part
        self.network = NetworkHandler()
        self.rotation_axis = np.array([0, 0, 1])

        # Graphic part
        pygame.init()
        self.display = (800, 600)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        self.scale_factor = 0.5

        self.eye = np.array([0, 0, 10])
        self.center = np.array([0, 0, 0])
        self.up = np.array([0, 1, 0])

        # Rotation parameters
        self.angle_degrees = 120
        self.rotation_axis = np.array([0, 1, 0])  # Rotate around the Y-axis

    def rotate_image(self, angle_degrees):
        self.network.scene.screen.base_vertices = [
            rotate_vector(vertex, angle_degrees, [0, 0, 1])
            for vertex in self.network.scene.screen.base_vertices
        ]

    def init_graphic(self):
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        rotated_eye = rotate_vector(self.eye, self.angle_degrees, self.rotation_axis)
        gluLookAt(rotated_eye[0], rotated_eye[1], rotated_eye[2], self.center[0], self.center[1], self.center[2],
                  self.up[0], self.up[1], self.up[2])

    def handle_pygame_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True, ClientViewer.EXIT
        return False, None

    def iteration(self):
        # Check for pygame events
        res, cmd = self.handle_pygame_events()
        if res:
            return cmd

        # Check for scene update
        if self.network.update:
            self.network.update = False

        # Draw scene
        self.draw_scene()

    def draw_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        rotated_eye = rotate_vector(self.eye, self.angle_degrees, self.rotation_axis)
        gluLookAt(rotated_eye[0], rotated_eye[1], rotated_eye[2], self.center[0], self.center[1], self.center[2],
                  self.up[0], self.up[1], self.up[2])

        if self.network.scene:
            self.network.scene.draw()

        pygame.display.flip()

    def handle(self):
        # Network thread startup
        thread = threading.Thread(target=self.network.handle)
        thread.start()
        self.init_graphic()

        while True:
            cmd = self.iteration()
            if cmd == ClientViewer.EXIT:
                break
            pygame.time.wait(10)


def main():
    cview = ClientViewer()
    cview.handle()


if __name__ == "__main__":
    main()