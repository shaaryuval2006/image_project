import select
import socket
import pygame
from master import protocol
import pickle


class ClientViewer:
    image_path = "images\\"
    def __init__(self, client_socket):

        self.pro = protocol.Protocol(client_socket)
        self.sock = client_socket
        self.screen = None
        self.surface = None
        self.py_image = None

        self.screen_w = 800
        self.screen_h = 800

    def close(self):
        self.sock.close()

    def receive_image(self):
        data_image = b''
        status, data = self.pro.get_msg()

        if status:
            im_d = pickle.loads(data)
            return status, im_d

        return status, data


    def receive_change(self):
        rlist, _, _ = select.select([self.sock], [], [], 0.01)
        if len(rlist) > 0:
            success, coordinates = self.pro.get_msg()
            print("Received coordinates string:", coordinates)
            if not success:
                print(f"Error: {coordinates}")
                return -1, None

            if not coordinates:
                print("Error: Received empty string for coordinates.")
                return -1, None

            coordinates = list(map(float, coordinates.split(b',')))
            print(coordinates, "hello5")
            return 0, coordinates
        return 1, "Timeout"

    def get_viewer_events(self):
        if not self.screen:

            pygame.init()

            self.screen = pygame.display
            self.surface = self.screen.set_mode((self.screen_w, self.screen_h))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            #print(event)

        return True

    def display_image(self, image, coordinates):

        self.py_image = pygame.image.frombuffer(image.tobytes(), (image.size[0], image.size[1]), 'RGB')
        transform_factor = self.screen_w / (coordinates[1] - coordinates[0])

        scale_xy = (int(self.py_image.get_width() * transform_factor),
                    int(self.py_image.get_height() * transform_factor))
        resized_image = pygame.transform.scale(self.py_image, scale_xy)

        white = (255, 255, 255)
        self.surface.fill(white)

        self.surface.blit(resized_image, (0, 0),
                          ( (int(coordinates[0])*transform_factor, (resized_image.get_height()-self.screen_h)/2, self.screen_w, self.screen_h)))

        self.screen.update()
        #pygame.display.flip()
        #print("Update done")


def main():
    ip = "127.0.0.1"
    port = 8000
    client_socket = socket.socket()
    client_socket.connect((ip, port))

    #res, data_image, status = protocol.Protocol(client_socket).get_msg()
    mycv = ClientViewer(client_socket)
    status, data = mycv.receive_image()

    if not status:
        print(f"bad message details ==> {data}")
        exit()

    pygame.init()
    last_coordinates = None
    not_done = True
    while not_done:
        #print("Get Data From Server.")
        # look for network event:
        status, coordinates = mycv.receive_change()
        if status == -1:
            print("connection closed!")
            not_done = False

        elif status == 0:
            last_coordinates = coordinates
            print("was change")
        else: # status 1 == timeout
            #print("No Data")
            pass

        # look for viewer event:
        if not mycv.get_viewer_events():
            not_done = False

        # refresh view
        if not_done:
            #print("Receiving image from the server...")
            mycv.display_image(data, last_coordinates)

    mycv.close()

if __name__ == "__main__":
    main()