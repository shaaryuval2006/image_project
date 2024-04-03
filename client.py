import socket
import pygame
import sys
import protocol
import pickle

image_path = "images\\"


def receive_image(client_socket):
    data_image = b''
    status, data_image, msg_status = protocol.Protocol(client_socket).get_msg()

    if status:
        im_d = pickle.loads(data_image)
        return status, im_d, msg_status

    return status, data_image, msg_status


def receive_coordinates(client_socket, protocol_instance):
    success, coordinates, _ = protocol_instance.get_msg()
    print("Received coordinates string:", coordinates)
    if not success:
        print(f"Error: {coordinates}")
        return None

    if not coordinates:
        print("Error: Received empty string for coordinates.")
        return None

    coordinates = list(map(float, coordinates.split(b',')))
    print(coordinates, "hello5")
    return coordinates


def display_image(image_details:protocol.ImageDetails, coordinates, client_socket):
    pygame.init()

    print(f"width_height = {image_details.w}-{image_details.h}, P")


    image = pygame.image.frombuffer(image_details.data, (image_details.w, image_details.h), 'RGB')
    screen_w = 800
    screen_h = 800
    screen = pygame.display.set_mode((screen_w, screen_h))

    transform_factor = screen_w / (coordinates[1] - coordinates[0])

    resized_image = pygame.transform.scale(image, (
    int(image.get_width() * transform_factor), int(image.get_height() * transform_factor)))

    screen.blit(resized_image, (0 - int(coordinates[0]) * transform_factor, 0))

    pygame.display.update()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()



def main():
    ip = "127.0.0.1"
    port = 8000
    client_socket = socket.socket()
    client_socket.connect((ip, port))

    protocol_instance = protocol.Protocol(client_socket)
    #res, data_image, status = protocol.Protocol(client_socket).get_msg()
    status, image_details, status_msg = receive_image(client_socket)

    if not status:
        print("bad message details")
        exit()

    while True:
        print("Image received successfully.")
        coordinates = receive_coordinates(client_socket, protocol_instance)
        print("Receiving image from the server...")

        display_image(image_details, coordinates, client_socket)


if __name__ == "__main__":
    main()