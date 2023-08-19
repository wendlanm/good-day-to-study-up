# Microservice implementation
# CS361 Summer 2023 Assignment 9
# Sheyar Abdullah

import time
import random
import os
import zmq


# Generates path to random image file in directory
def generate_image_path():
    dir = "./images"
    images = os.listdir(dir)
    index = random.randrange(len(images))
    return os.path.join(dir, images[index])

# Initialize microservice socket
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    # Wait for request
    message = socket.recv()
    print(f"Received request: {message}")

    if message == b"get_image":
        image_path = generate_image_path()
        socket.send(image_path.encode())

    time.sleep(0.2)
