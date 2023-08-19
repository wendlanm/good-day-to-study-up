import zmq
import os


def get_one_image():
    # Initialize socket
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    image_path = ""
    while image_path[-4:] != ".jpg":
        # Request random imagepath
        socket.send(b"get_image")

        # Receive reply
        image_path = socket.recv()
        image_path = image_path.decode('utf-8')
    return os.path.join("microservice", image_path[2:])
