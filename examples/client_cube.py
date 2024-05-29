import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import socket
import pickle
import threading
import time
import protocol
import scene



def receive_cube_position(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)
            position = pickle.loads(data)
            return position
        except (ConnectionResetError, EOFError, pickle.UnpicklingError):
            break

def client_thread():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 9999))



    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(120, (display[0] / display[1]), 0.1, 50.0)
    gluLookAt(0, 0, 0, 0, 0, -5, 0, 1, 0)

    scale_factor = 0.5
    position = receive_cube_position(client_socket)
    last_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        current_time = time.time()
        if current_time - last_time >= 0.1:
            glTranslatef(0.1, 0.0, 0.0)
            last_time = current_time

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()  # Save the current matrix
        glTranslatef(*position)
        glScalef(scale_factor, scale_factor, scale_factor)  # Scale the cube
        Cube(0)  # Draw the scaled cube
        glPopMatrix()  # Restore the previous matrix

        pygame.display.flip()
        pygame.time.wait(10)

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
                # parse data message ... result with cmd, params
                params = []
                cmd = "SCENE"
                if cmd == "SCENE":
                    self.scene = pickle.loads(params[0])
                    self.update = True
                pass # do something with data received
                # scale_factor = 0.5
                # position = receive_cube_position(client_socket)
                # last_time = time.time()

class ClientViewer:
    EXIT = 0
    def __init__(self):
        #network part
        self.network = NetworkHandler()

        # graphic part
        pygame.init()
        self.display = (800, 600)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)

        # ORIENTATION:
        self.position =

    def init_graphic(self):
        gluPerspective(120, (self.display[0] / self.display[1]), 0.1, 50.0)
        gluLookAt(0, 0, 0, 0, 0, -5, 0, 1, 0)

    def handle_pygame_events(self) -> (bool, int):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True, ClientViewer.EXIT
                #exit program



    def iteration(self):
        # check for pygame events
        res, cmd = self.handle_pygame_events()
        # get scene update
            # check if there was a scene update... check data
            # if so update data

        # draw scene update
        pass

    def draw_scene(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()  # Save the current matrix
        glTranslatef(*position)
        glScalef(scale_factor, scale_factor, scale_factor)  # Scale the cube
        Cube(0)  # Draw the scaled cube
        glPopMatrix()  # Restore the previous matrix

        pygame.display.flip()

    def handle(self):
        # network thread startup
        thread = threading.Thread(target=self.network.handle)
        self.init_graphic()
        while True:
            #....
            self.iteration()
            pygame.time.wait(10)


def main():
    cview = ClientViewer()
    ClientViewer.handle()

if __name__ == "__main__":
    main()
