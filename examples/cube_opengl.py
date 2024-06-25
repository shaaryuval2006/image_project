import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Define the vertices and edges of the cube
vertices = [
    [1, 1, -1],
    [1, -1, -1],
    [-1, -1, -1],
    [-1, 1, -1],
    [1, 1, 1],
    [1, -1, 1],
    [-1, -1, 1],
    [-1, 1, 1]
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

def draw_cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    clock = pygame.time.Clock()
    angle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        angle += 1  # Increase the rotation angle

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glRotatef(angle, 3, 1, 1)  # Rotate the cube around the x, y, and z axes
        draw_cube()
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second


def main2():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)  # Enable depth testing

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    # Initialize camera and cube position
    camera_position = [0, 0, 0]
    cube_position = [0, 0, 5]

    clock = pygame.time.Clock()
    angle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        angle += 1  # Increase the rotation angle

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up the view matrix
        glLoadIdentity()
        gluLookAt(camera_position[0], camera_position[1], camera_position[2],  # camera position
                  0, 0, 0,  # look at origin
                  0, 1, 0)  # up vector

        # Translate the cube to its position
        glTranslatef(cube_position[0], cube_position[1], cube_position[2])

        # Rotate around its own axis
        glRotatef(angle, 0, 1, 0)

        draw_cube()  # Draw the cube
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second




if __name__ == "__main__":
    main2()
