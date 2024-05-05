import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Three 3D Cubes")

# Colors
BLACK = (0, 0, 0)
WHITE = (25, 255, 255)

# Cube vertices (scaled)
vertices = [
    (-50, -50, -50),
    (50, -50, -50),
    (50, 50, -50),
    (-50, 50, -50),
    (-50, -50, 50),
    (50, -50, 50),
    (50, 50, 50),
    (-50, 50, 50)
]

# Define edges by connecting vertices
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# Define center and angle of rotation for the first cube
center1 = [WIDTH // 4, HEIGHT // 2]
angle = 0

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    # Rotation matrix functions
    def rotate_x(vertex, angle):
        x, y, z = vertex
        rad = math.radians(angle)
        new_y = y * math.cos(rad) - z * math.sin(rad)
        new_z = y * math.sin(rad) + z * math.cos(rad)
        return x, new_y, new_z

    def rotate_y(vertex, angle):
        x, y, z = vertex
        rad = math.radians(angle)
        new_x = x * math.cos(rad) + z * math.sin(rad)
        new_z = -x * math.sin(rad) + z * math.cos(rad)
        return new_x, y, new_z

    # Rotate and scale cube vertices for the first cube
    rotated_vertices = [(x * 2, y * 2, z * 2) for x, y, z in vertices]
    rotated_vertices1 = [rotate_y(rotate_x(vertex, angle), angle) for vertex in rotated_vertices]

    # Draw edges for the first cube
    for edge in edges:
        start = rotated_vertices1[edge[0]]
        end = rotated_vertices1[edge[1]]
        pygame.draw.line(screen, WHITE, (start[0] + center1[0], start[1] + center1[1]), (end[0] + center1[0], end[1] + center1[1]))

    # Define center for the second cube (other side of the screen)
    center2 = [WIDTH // 2, HEIGHT // 2]

    # Rotate and scale cube vertices for the second cube
    rotated_vertices2 = [(x * 2, y * 2, z * 2) for x, y, z in vertices]
    rotated_vertices2 = [rotate_y(rotate_x(vertex, angle), angle) for vertex in rotated_vertices2]

    # Draw edges for the second cube
    for edge in edges:
        start = rotated_vertices2[edge[0]]
        end = rotated_vertices2[edge[1]]
        pygame.draw.line(screen, WHITE, (start[0] + center2[0], start[1] + center2[1]), (end[0] + center2[0], end[1] + center2[1]))

    # Define center for the third cube (left side of the screen)
    center3 = [WIDTH // 4, HEIGHT // 2]

    # Rotate and scale cube vertices for the third cube
    rotated_vertices3 = [(x * 2, y * 2, z * 2) for x, y, z in vertices]
    rotated_vertices3 = [rotate_y(rotate_x(vertex, angle), angle) for vertex in rotated_vertices3]

    # Draw edges for the third cube
    for edge in edges:
        start = rotated_vertices3[edge[0]]
        end = rotated_vertices3[edge[1]]
        pygame.draw.line(screen, WHITE, (start[0] + center3[0], start[1] + center3[1]), (end[0] + center3[0], end[1] + center3[1]))

    angle += 1  # Rotate all cubes

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # Cap the frame rate
