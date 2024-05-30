# scene.py

from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

class Screen:
    def __init__(self, delta):
        self.vertices = (
            (1 + delta, -0.75 + delta, -1 + delta),
            (1 + delta, 0.75 + delta, -1 + delta),
            (-1 + delta, 0.75 + delta, -1 + delta),
            (-1 + delta, -0.75 + delta, -1 + delta)
        )

        self.texture_name = r'..\stitched_image_without_pillow2.png'
        self.texture = Image.open(self.texture_name)
        if self.texture.mode != 'RGBA':
            self.texture = self.texture.convert('RGBA')
        self.texture_data = self.texture.tobytes()
        self.texture_cords = ((0, 0), (0, 1), (1, 1), (1, 0))

    def draw(self):
        texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.texture.width, self.texture.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, self.texture_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glEnable(GL_TEXTURE_2D)
        print("Drawing screen")
        glBegin(GL_QUADS)
        glNormal3d(0, 0, 1)

        for i in range(4):
            glTexCoord2f(self.texture_cords[i][0], self.texture_cords[i][1])
            glVertex3fv(self.vertices[i])

        glEnd()
        glDisable(GL_TEXTURE_2D)



class Cube:
    def __init__(self, delta):
        self.vertices = (
            (1 + delta, -1 + delta, -1 + delta),
            (1 + delta, 1 + delta, -1 + delta),
            (-1 + delta, 1 + delta, -1 + delta),
            (-1 + delta, -1 + delta, -1 + delta),
            (1 + delta, -1 + delta, 1 + delta),
            (1 + delta, 1 + delta, 1 + delta),
            (-1 + delta, -1 + delta, 1 + delta),
            (-1 + delta, 1 + delta, 1 + delta)
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
        print("Drawing cube")  # Add this line
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()


class Scene:
    def __init__(self, delta_list):
        #self.objs = [Cube(delta) for delta in delta_list]
        self.objs = []
        for delta in delta_list:
            self.objs.append(Cube(delta))
        self.objs.append(Screen(1))

    def draw(self):
        for obj in self.objs:
            obj.draw()
