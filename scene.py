# scene.py

from OpenGL.GL import *
from OpenGL.GLU import *

class Cube:
    def __init__(self, delta):
        self.vertices = (
            (1 + delta, -1 + delta, -1 + delta + 5),
            (1 + delta, 1 + delta, -1 + delta + 5),
            (-1 + delta, 1 + delta, -1 + delta + 5),
            (-1 + delta, -1 + delta, -1 + delta + 5),
            (1 + delta, -1 + delta, 1 + delta + 5),
            (1 + delta, 1 + delta, 1 + delta + 5),
            (-1 + delta, -1 + delta, 1 + delta + 5),
            (-1 + delta, 1 + delta, 1 + delta + 5)
        )

        self.edges = (
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

    def draw(self):
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()


class Scene:
    def __init__(self, positions):
        self.cubes = [Cube(delta) for delta in positions]

    def draw(self):
        for cube in self.cubes:
            cube.draw()
