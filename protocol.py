import socket


# <length><data>
class Protocol:
    MESSAGE_LENGTH = 10
    def __init__(self, c_s):
        self.current_socket = c_s

    def get_msg(self) -> (bool, bytes):
        data = self.current_socket.recv(Protocol.MESSAGE_LENGTH).decode()
        if data == b"":
            return False, "Connection Error"

        if not data.isnumeric():
            return False, "Message Error"

        datalen = int(data)

        data = self.current_socket.recv(datalen)
        if data == b"":
            return False, "Connection Error"

        while len(data) < datalen:
            extra = b""
            extra = self.current_socket.recv(datalen - len(data))
            if extra == b"":
                return False, "Connection Error"

            data += extra

        return True, data

    def create_msg(self, data: bytes):
        datalen = len(data)
        msg = str(datalen).zfill(self.MESSAGE_LENGTH).encode() + data
        return msg


    def check_msg(self):
        pass

class ImageDetails:
    def __init__(self, h,w,data):
        self.h = h
        self.w = w
        self.data = data