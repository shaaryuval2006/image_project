import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import numpy as np
import pickle
import socket
import protocol
from scene import Scene
import math

class SceneDisplayClient:
    def __init__(self):
        self.scene_locker = threading.Lock()
        self.scene = None
        self.next_scene = None
        self.whoami = -1

        self.display = (800, 600)  # Desired display resolution
        self.rotation_axis = np.array([0, 1, 0])
        self.fov = 120  # Initial FOV

        self.client_id = None
        self.server_ip = None
        self.server_port = None
        self.motion = 0

        pygame.init()
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        self.init_graphic()
        self.proto = protocol.Protocol(None)  # Initialize the protocol without a socket for now

        self.server_thread = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #glLoadIdentity()
        if self.scene:
            glPushMatrix()
            glRotatef(self.scene.line_of_sight_angle, self.rotation_axis[0], self.rotation_axis[1], self.rotation_axis[2])
            self.scene.draw()
            glPopMatrix()

        pygame.display.flip()

    def reshape(w, h):
        glViewport(0, 0, 800, 600)

    def receive_server_actions(self):
        self.server_socket.connect((self.server_ip, self.server_port))
        self.proto = protocol.Protocol(self.server_socket)
        message = self.proto.create_msg(pickle.dumps(("screen_connect", self.client_id, self.whoami)))
        self.server_socket.sendall(message)

        while True:
            res, msg = self.proto.get_msg()
            if res:
                print(f"res = {res}, msg_len = {len(msg)}")
                cmd, data = pickle.loads(msg)
                if cmd == "scene":
                    scene_data = pickle.loads(data)  # Deserialize the scene data
                    if isinstance(scene_data, Scene):
                        with self.scene_locker:
                            self.next_scene = scene_data

    def rotate_around_center_lookAt(self, angle):
        radius = 5.0  # Radius of the orbit
        bigradius = math.sqrt(radius * radius + radius * radius)
        angle_rad = math.radians(angle)
        eye_x = radius * math.cos(angle_rad)
        eye_z = radius * math.sin(angle_rad)
        # eye_y = math.sqrt(bigradius*bigradius - eye_x * eye_x - eye_z*eye_z)
        gluLookAt(0, 0, 0, -eye_x, 0, -eye_z, 0, 1, 0)
    def receive_main_client_action(self):  # waiting for main client
        screen_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        screen_server_socket.bind(("0.0.0.0", 8889))
        screen_server_socket.listen(5)

        while True:
            client_socket, addr = screen_server_socket.accept()
            try:
                self.proto = protocol.Protocol(client_socket)
                res, msg = self.proto.get_msg()
                if res:
                    if self.client_id is None or self.server_ip is None or self.server_port is None:
                        client_info = pickle.loads(msg)
                        self.client_id, self.server_ip, self.server_port, self.whoami , self.motion = client_info
                        print(f"Client ID: {self.client_id}, Server IP: {self.server_ip}, Server Port: {self.server_port}, motion = {self.motion}")

                        # start thread with server:
                        # 1. Send the client ID to the server
                        # 2. wait for commands...
                        if self.server_thread is None:
                            self.server_thread = threading.Thread(target=self.receive_server_actions)
                            self.server_thread.start()

            except (ConnectionResetError, EOFError) as e:
                print(f"Connection lost with the client: {e}")
                break
            client_socket.close()
        screen_server_socket.close()

    def start_viewer(self):
        scene_thread = threading.Thread(target=self.receive_main_client_action)
        scene_thread.start()

        while True:
            if self.handle_pygame_events():
                break
            if self.motion != 0 and self.scene is not None:  # Check if self.scene is not None
                self.scene.set_motion(self.motion)
                self.motion = 0
            with self.scene_locker:
                if self.next_scene is not None:
                    self.scene = self.next_scene
                    self.next_scene = None
            if self.scene is not None:  # Ensure self.scene is not None before drawing
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(self.scene.fov, (self.display[0] / self.display[1]), 0.1, 50.0)

                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                self.rotate_around_center_lookAt(self.scene.line_of_sight_angle)
                self.draw_scene()
            pygame.time.wait(100)


if __name__ == "__main__":
    viewer = SceneDisplayClient()
    viewer.start_viewer()