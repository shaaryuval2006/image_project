
from PIL import Image
from OpenGL.GL import *



class Screen:
    def __init__(self, delta, texture_coords, translation, width_scale=6, height_scale=6):
        self.translation = translation
        self.delta = delta
        self.width_scale = width_scale
        self.height_scale = height_scale
        self.offset_x = 0
        self.motion_step = 0

        self.base_vertices = (
            (self.width_scale / 2 + self.delta, -self.height_scale / 2 + self.delta, -1 + self.delta),
            (self.width_scale / 2 + self.delta, self.height_scale / 2 + self.delta, -1 + self.delta),
            (-self.width_scale / 2 + self.delta, self.height_scale / 2 + self.delta, -1 + self.delta),
            (-self.width_scale / 2 + self.delta, -self.height_scale / 2 + self.delta, -1 + self.delta)
        )
        self.vertices = self.base_vertices
        self.texture_name = r'..\black_air_plain.png'
        self.texture = Image.open(self.texture_name)
        if self.texture.mode != 'RGBA':
            self.texture = self.texture.convert('RGBA')
        self.texture_data = self.texture.tobytes()
        self.texture_coords = texture_coords
          # Add an offset for the x-axis

    def draw(self):
        self.offset_x += self.motion_step
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
        glRotate(20,0,0, 0)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glNormal3d(0, 0, 1)

        # Updated section: incorporating x_offset
        glColor3f(1.0, 1.0, 1.0)
        for i in range(4):
            x, y, z = self.base_vertices[i]
            glTexCoord2f(self.texture_coords[i][0], self.texture_coords[i][1])
            glVertex3f(x + self.offset_x + self.translation[0],
                       y + self.translation[1],
                       z + self.translation[2])

        glEnd()
        glDisable(GL_TEXTURE_2D)


class Cube_X:
    def __init__(self, delta, translation=(0, 0, 0)):
        self.translation = translation
        self.offset_x = 0
        self.motion_step = 0
        self.vertices = (
            (1 + delta, -1 + delta, -1 + delta),
            (1 + delta, 1 + delta, -1 + delta),
            (-1 + delta, 1 + delta, -1 + delta),
            (-1 + delta, -1 + delta, -1 + delta),
            (1 + delta, -1 + delta, 1 + delta),
            (1 + delta, 1 + delta, 1 + delta),
            (-1 + delta, 1 + delta, 1 + delta),
            (-1 + delta, -1 + delta, 1 + delta)
        )

        self.edges = (
            (0, 1), # 0
            (1, 2), # 1
            (2, 3), # 2
            (3, 0), # 3
            (4, 5), # 4
            (5, 6), # 5
            (6, 7), # 6
            (7, 4), # 7
            (0, 4), # 8
            (1, 5), # 9
            (2, 6), # 10
            (3, 7)  # 11
        )

        self.faces = (
            ((0, 0), (1, 0), (2, 0), (3, 0)),  # Front face
            ((4, 0), (5, 0), (6, 0), (7, 0)),  # Back face
            ((1, 0), (10, 0), (5, 1), (9, 1)),  # Top face
            ((3, 1), (11, 0), (7, 0), (8, 1)),  # Bottom face
            ((2, 1), (10, 0), (6, 0), (11, 1)),  # Right face
            ((0, 0), (9, 0), (4, 1), (8, 1))   # Left face
        )

        self.face_colors = (
            (1, 0, 0),
            (0, 1, 1),
            (0, 0, 1),
            (0, 0, 1),
            (0, 1, 1),
            (1, 0, 1)
        )
    def draw(self):

        glBegin(GL_QUADS)
        i_face = 0
        self.offset_x -= self.motion_step
        for face in self.faces:
            glColor3f(self.face_colors[i_face][0], self.face_colors[i_face][1], self.face_colors[i_face][2])
            i_face += 1
            for edge_map in face:
                edge_id, vertex_in_edge = edge_map
                vertex = self.edges[edge_id][vertex_in_edge]
                glVertex3f(self.vertices[vertex][0] + self.translation[0] + self.offset_x,
                           self.vertices[vertex][1] + self.translation[1],
                           self.vertices[vertex][2] + self.translation[2])
        glEnd()

        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3f(self.vertices[vertex][0] + self.translation[0] + self.offset_x,
                           self.vertices[vertex][1] + self.translation[1],
                           self.vertices[vertex][2] + self.translation[2])
        glEnd()


class Cube:
    def __init__(self, delta, translation=(0, 0, 0)):
        self.translation = translation
        self.offset_x = 0
        self.motion_step = 0
        self.vertices = (
            (1 + delta, -1 + delta, -1 + delta),
            (1 + delta, 1 + delta, -1 + delta),
            (-1 + delta, 1 + delta, -1 + delta),
            (-1 + delta, -1 + delta, -1 + delta),
            (1 + delta, -1 + delta, 1 + delta),
            (1 + delta, 1 + delta, 1 + delta),
            (-1 + delta, 1 + delta, 1 + delta),
            (-1 + delta, -1 + delta, 1 + delta)
        )

        self.edges = (
            (0, 1), # 0
            (1, 2), # 1
            (2, 3), # 2
            (3, 0), # 3
            (4, 5), # 4
            (5, 6), # 5
            (6, 7), # 6
            (7, 4), # 7
            (0, 4), # 8
            (1, 5), # 9
            (2, 6), # 10
            (3, 7)  # 11
        )

        self.faces = (
            ((0, 0), (1, 0), (2, 0), (3, 0)),  # Front face
            ((4, 0), (5, 0), (6, 0), (7, 0)),  # Back face
            ((1, 0), (10, 0), (5, 1), (9, 1)),  # Top face
            ((3, 1), (11, 0), (7, 0), (8, 1)),  # Bottom face
            ((2, 1), (10, 0), (6, 0), (11, 1)),  # Right face
            ((0, 0), (9, 0), (4, 1), (8, 1))   # Left face
        )

        self.face_colors = (
            (1, 0, 0),
            (0, 1, 1),
            (0, 0, 1),
            (0, 0, 1),
            (0, 1, 1),
            (1, 0, 1)
        )
    def draw(self):

        glBegin(GL_QUADS)
        i_face = 0
        for face in self.faces:
            glColor3f(self.face_colors[i_face][0], self.face_colors[i_face][1], self.face_colors[i_face][2])
            i_face += 1
            for edge_map in face:
                edge_id, vertex_in_edge = edge_map
                vertex = self.edges[edge_id][vertex_in_edge]
                glVertex3f(self.vertices[vertex][0] + self.translation[0],
                           self.vertices[vertex][1] + self.translation[1],
                           self.vertices[vertex][2] + self.translation[2])
        glEnd()

        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3f(self.vertices[vertex][0] + self.translation[0],
                           self.vertices[vertex][1] + self.translation[1],
                           self.vertices[vertex][2] + self.translation[2])
        glEnd()


class Scene:
    #                  texture_coords =((0, 0.2), (0.2, 1), (1, 0.8), (0.8, 0))
    #                  texture_coords =((0, 0), (0, 1), (1, 0), (1, 1))
    def __init__(self, texture_coords =((0, 0.02), (0.02, 1), (1, 0.98), (0.98, 0)), line_of_sight_angle=0, fov=120):
        self.objs = []
        self.motion = 0

        translations_cube = (
            # (5, 0, 0),
            # (-5, 0, 0),
            # (10, 0, 0),
            # (-10, 0, 0),
            # (0, 5, 0),
            # (0, -5, 0),
            # (0, 10, 0),
            # (0, -10, 0),
            # (0, 0, 5),
            # (0, 0, -5),
            # (0, 0, 10),
            # (0, 0, -10),
            # (0, 10, 5),
            # (0, 10, -5),
            # (0, 10, 10),
            # (0, 10, -10),
            (-2, 0, 5),
            (-3, 0, -5),
            (-4, 0, 10),
            (-5, 0, -10),
        )

        translations_screen = (
            # (1, 0, 5),
            (2, 0, -5),
            # (3, 0, 10),
            # (4, 0, -10),
        )

        translations_cube_stati = (
            (0, 10, -10),
        )
        self.cubes = []
        self.screens = []

        for t in translations_cube:
            self.cubes.append(Cube_X(0, t))

        for t in translations_screen:
            self.screens.append(Screen(0, texture_coords, t))

        for t in translations_cube_stati:
            self.cubes.append(Cube(0, t))

        for cube in self.cubes:
            self.objs.append(cube)

        for screen in self.screens:
            self.objs.append(screen)

        self.line_of_sight_angle = line_of_sight_angle
        self.fov = fov

    def set_motion(self, motion):
        print(f"new motion = {motion}")
        for obj in self.objs:
            obj.motion_step = motion

    def draw(self):
        glPushMatrix()
        for obj in self.objs:
            obj.draw()
        glPopMatrix()

    def update_x_offset(self, offset):
        self.screens.x_offset = offset