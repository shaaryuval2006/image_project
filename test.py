from PIL import Image
import socket
import threading
import time
from protocol import Protocol, ImageDetails
from numpy import asarray
import pickle

class Serverhandler:
    def __init__(self):
        self.number_of_clients = 0
        self.server_socket = socket.socket()
        self.server_socket.bind(("0.0.0.0", 8000))
        self.server_socket.listen(5)
        self.input_path = None
        self.clients = []
        self.img = None
        self.numpydata = asarray(self.img)
        print("Waiting for connections...")

    def read_file_chuncs(self, image_path):
        chunks = []
        with open(image_path, 'rb') as file:

            data = file.read(1024)
            while data:
                chunks.append(data)
                data = file.read(1024)

        return chunks
    def handler(self):
        self.input_path = "stitched_image_without_pillow2.png"
        #image_file_chunks = self.read_file_chuncs(self.input_path)
        self.img = Image.open(self.input_path)

        size = self.img.size
        format = self.img.getbands()
        whay = self.img.format
        bytes_data = self.img.tobytes()



        while True:
            client_socket, client_address = self.server_socket.accept()
            self.number_of_clients += 1



            #print("client added... -> number of clients:", self.number_of_clients)

            ch = ClientHandler(client_socket, client_address, self.number_of_clients, self.img.tobytes(), size, self.img)
            self.clients.append(ch)

            parts = diller(self.img.width, self.number_of_clients)

            if self.number_of_clients >= 4:
                for i in range(self.number_of_clients-1):
                    self.clients[i].my_part = parts[i]
                    self.clients[i].was_change = True


            ch.my_part = parts[self.number_of_clients-1]

            client_t = threading.Thread(target=ch.handler, daemon=True)
            client_t.start()


class ClientHandler:
    def __init__(self, client_socket, client_address, client_id, image_chunks, size, img):
        self.s = client_socket
        self.protocol = Protocol(client_socket)
        self.client_address = client_address
        self.client_id = client_id
        self.my_part = None
        #self.image = image
        self.image_chunks = image_chunks
        self.size = size
        self.img = img
        self.was_change = False

    def handler(self):
        input_path = "stitched_image_without_pillow2.png"
        self.send_image()
        self.send_coordinates(input_path)
        #print(f"Sending image to {self.client_address}")


        while True:
            if self.was_change:
                self.send_coordinates(input_path)
                self.was_change = False

        self.s.close()
        print(f"Connection from {self.client_address} closed")

    def send_coordinates(self, input_path):
        #print("number of clients:")
        starting_point = self.my_part[0]
        ending_point = self.my_part[1]
        coordinates = (starting_point, ending_point)
        #print(coordinates, "works")
        coordinates_str = f"{coordinates[0]},{coordinates[1]}"
        print(f"Sending coordinates: {coordinates_str}")
        msg = self.protocol.create_msg(coordinates_str.encode())
        self.protocol.current_socket.send(msg)

    def send_image(self):
        #im_d = ImageDetails(self.size[0], self.size[1], self.image_chunks)
        #im_d_data = pickle.dumps(im_d)
        im_d_data = pickle.dumps(self.img)
        msg = Protocol(self.s).create_msg(im_d_data)
        #print("msg is -----   ", msg)

        self.s.send(msg)


def diller(width: int, n: int) ->list:
    if n == 1:
        return [(0, width//3)]
    if n == 2:
        return [(0, width//3), (width//3, (2*width//3))]

    part_width = width / n
    my_res = []
    for i in range(n):
        my_res.append((int(i*part_width), int((i+1)*part_width)))

    return my_res





def main():
    myserver = Serverhandler()
    myserver.handler()


if __name__ == "__main__":
    main()
