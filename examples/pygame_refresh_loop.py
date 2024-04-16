# import pygame module
import pygame

pygame.init()

# width
width = 680

# height
height = 480

# store he screen size
z = [width, height]

# store the color
white = (255, 255, 255)
screen_display = pygame.display

# Set caption of screen
screen_display.set_caption('GEEKSFORGEEKS')

# setting the size of the window
surface = screen_display.set_mode(z)

# set the image which to be displayed on screen
python = pygame.image.load(r'C:\cyber\pyptojects\image_project\stitched_image_without_pillow2.png')

# set window true
window = True
while window:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            window = False

            # display white on screen other than image
    surface.fill(white)

    # draw on image onto another
    surface.blit(python, (0, 0), (0, 500, python.get_width(), python.get_height()))
    surface.blit(python, (0, 100), (20, 20, 50, 20))

    screen_display.update()

pygame.quit()