import socket
from source.pbc.pbc_utils import logger

class PbSocket(object):
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))

    def __del__(self):
        pass

    def send_message(self, encoded_protobuf):
        encoded_protobuf_length = len(encoded_protobuf).to_bytes(4, byteorder="little")
        logger.info("Encoded protobuf message length: {}".format(len(encoded_protobuf)))
        self.sock.sendall(encoded_protobuf_length + encoded_protobuf)

    def _recv_exactly(self, n):
        buf = bytearray()
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise OSError("Socket closed before all bytes were received.")
            buf.extend(chunk)
        return bytes(buf)

    def receive_message(self):
        encoded_protobuf_length = self._recv_exactly(4)
        length = int.from_bytes(encoded_protobuf_length, byteorder='little')
        encoded_protobuf = self._recv_exactly(length)
        return encoded_protobuf

# import socket
# from source.pbc.pbc_utils import logger


# class PbSocket(object):
#     def __init__(self, ip, port):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.connect((ip, port))

#     def __del__(self):
#         pass

#     def send_message(self, encoded_protobuf):
#         encoded_protobuf_length = len(encoded_protobuf).to_bytes(4, byteorder="little")
#         logger.info("Encoded protobuf message length: {}".format(len(encoded_protobuf)))
#         self.sock.sendall(encoded_protobuf_length + encoded_protobuf)

#     def receive_message(self):
#         encoded_protobuf_length = self.sock.recv(4)
#         encoded_protobuf = self.sock.recv(int.from_bytes(encoded_protobuf_length, byteorder='little'))
#         return encoded_protobuf