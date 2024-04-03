from PIL import Image
import matplotlib.pyplot as plt
import pygame
import sys
import socket


server_socket = socket.socket()
server_socket.bind(("0.0.0.0", 8000))
server_socket.listen(1)


def extract_first_20_pixels(input_path, output_path):
    a = 0
    b = 0
    c = 20
    image = Image.open(input_path)

    first_part = image.crop((a, b, c, image.height))
    first_part.save(output_path)

    return image, first_part, a, b, c

def main():
    pygame.init()  # Initialize Pygame

    input_path = "stitched_image_without_pillow2.png"
    output_path = "stitched_image_first_20px.png"

    image, first_part, a, b, c = extract_first_20_pixels(input_path, output_path)
    image = Image.open(input_path)
    w = image.width

    # Display the initial image
    X = 800
    Y = 600
    a = 0
    b = 0

    # create the display surface object of specific dimension (X, Y).
    scrn = pygame.display.set_mode((X, Y))

    # set the pygame window name
    pygame.display.set_caption('image')

    # create a surface object, image is drawn on it.
    imp = pygame.image.load(input_path).convert()

    scrn.blit(imp, (a, b))
    scrn.blit(imp, (a + w, b))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    a = (a + 20) % w - w
                    b = 0
                    scrn.blit(imp, (a, b))
                    scrn.blit(imp, (a + w, b))
                    pygame.display.flip()

                elif event.key == pygame.K_LEFT:
                    a = (a - 20) % w - w
                    b = 0
                    scrn.blit(imp, (a, b))
                    scrn.blit(imp, (a + w, b))
                    pygame.display.flip()

if __name__ == "__main__":
    main()
