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

        # Graphic part
        pygame.init()
        self.display = (800, 600)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        self.scale_factor = 0.5

    def init_graphic(self):
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)

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
        gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)

        print("start scene")
        if self.network.scene:
            self.network.scene.draw()
        print("end_scene ...\n")


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
