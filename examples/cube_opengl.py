import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time

def Cube(delta):
    vertices = (
        (1 + delta, -1 + delta, -1 + delta + 5),
        (1 + delta, 1 + delta, -1 + delta + 5),
        (-1 + delta, 1 + delta, -1 + delta + 5),
        (-1 + delta, -1 + delta, -1 + delta + 5),
        (1 + delta, -1 + delta, 1 + delta + 5),
        (1 + delta, 1 + delta, 1 + delta + 5),
        (-1 + delta, -1 + delta, 1 + delta + 5),
        (-1 + delta, 1 + delta, 1 + delta + 5)
    )

    edges = (
        (0, 1),
        (0, 3),
        (0, 4),
        (2, 1),
        (2, 3),
        (2, 7),
        (6, 3),
        (6, 4),
        (6, 7),
        (5, 1),
        (5, 4),
        (5, 7)
    )
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def move_cube_right(speed):
    glTranslatef(speed, 0.0, 0.0)

def set_cube_position_top_left():
    glTranslatef(-4.0, 3.0, -5)

def set_cube_position_bottom_left():
    glTranslatef(-8.0, 0.0, -5)

def set_cube_position_right():
    glTranslatef(-2.0, 0.0, -5)

def move_cube_up(speed):
    glTranslatef(0.0, speed, 0.0)


def move_cube_in(speed):
    glTranslatef(0.0, 0.0, speed)


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(120, (display[0] / display[1]), 0.1, 50.0)
    gluLookAt(0, 0, 0, 0, 0, -5, 0, 1, 0)

    set_cube_position_top_left()

    scale_factor = 0.5

    last_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        current_time = time.time()
        if current_time - last_time >= 0.1:
            move_cube_right(0.1)
            last_time = current_time


        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()  # Save the current matrix
        glScalef(scale_factor, scale_factor, scale_factor)  # Scale the cube
        Cube(0)  # Draw the scaled cube
        glPopMatrix()  # Restore the previous matrix

        pygame.display.flip()
        pygame.time.wait(10)

main()
