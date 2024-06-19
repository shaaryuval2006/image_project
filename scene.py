from OpenGL.GL import *
#from OpenGL.GLU import *
from PIL import Image


class Screen:
    def __init__(self, delta, texture_coords, width_scale=4.5, height_scale=4.5):
        self.delta = delta
        self.width_scale = width_scale
        self.height_scale = height_scale
        self.base_vertices = (
            (self.width_scale / 2 + self.delta-25, -self.height_scale / 2 + self.delta, -1 + self.delta),
            (self.width_scale / 2 + self.delta-25, self.height_scale / 2 + self.delta, -1 + self.delta),
            (-self.width_scale / 2 + self.delta-25, self.height_scale / 2 + self.delta, -1 + self.delta),
            (-self.width_scale / 2 + self.delta-25, -self.height_scale / 2 + self.delta, -1 + self.delta)
        )
        self.vertices = self.base_vertices
        self.texture_name = r'..\stitched_image_without_pillow2.png'
        self.texture = Image.open(self.texture_name)
        if self.texture.mode != 'RGBA':
            self.texture = self.texture.convert('RGBA')
        self.texture_data = self.texture.tobytes()
        self.texture_coords = texture_coords
        self.x_offset = 0.1  # Add an offset for the x-axis

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
        glBegin(GL_QUADS)
        glNormal3d(0, 0, 1)

        # Updated section: incorporating x_offset
        for i in range(4):
            x, y, z = self.base_vertices[i]
            glTexCoord2f(self.texture_coords[i][0], self.texture_coords[i][1])
            glVertex3f(x + self.x_offset, y, z)

        glEnd()
        glDisable(GL_TEXTURE_2D)



class Cube:
    def __init__(self, delta, translation=(0, 0, 0)):
        self.translation = translation
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
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3f(self.vertices[vertex][0] + self.translation[0],
                           self.vertices[vertex][1] + self.translation[1],
                           self.vertices[vertex][2] + self.translation[2])
        glEnd()


class Scene:
    def __init__(self, texture_coords =((0, 0), (0, 1), (1, 0), (1, 1)), line_of_sight_angle=0, fov=120):
        self.objs = []
        self.screen = Screen(0, texture_coords)
        # Position the first cube on the left
        self.cube1 = Cube(0, translation=(5, 0, 0))
        # Position the second cube on the right
        self.cube2 = Cube(0, translation=(-5, 0, 0))
        self.cube3 = Cube(0, translation=(0, 0, -5))
        # Position the second cube on the right
        self.cube4 = Cube(0, translation=(0, 0, 5))

        self.objs.append(self.screen)
        self.objs.append(self.cube1)
        self.objs.append(self.cube2)
        self.objs.append(self.cube3)
        self.objs.append(self.cube4)
        self.line_of_sight_angle = line_of_sight_angle
        self.fov = fov

    def draw(self):
        glPushMatrix()
        #glRotatef(self.rotation_angle, 0, 1, 0)  # Rotate around the Y-axis
        for obj in self.objs:
            obj.draw()
        glPopMatrix()

    def update_x_offset(self, offset):
        self.screen.x_offset = offset