# Example microservice client implementation
# CS361 Summer 2023 Assignment 9
# Michael Wendland

import zmq
import time
import json


def convert_dict_to_bytes(input_dict):
    return str(input_dict).encode()


context = zmq.Context()

# Initialize socket to talk to microservice
print("Connecting to leaderboard microservice...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:8888")
print("Connected!")

# Request the current leaderboard
print("Sending request for current leaderboard")
socket.send(b"get_leaderboard")

# Get the reply
leaderboard_data = socket.recv()
leaderboard_data = leaderboard_data.decode('utf-8').replace("\'", "\"")
json_data = json.loads(leaderboard_data)
print(f"type: {type(json_data)}")
print(f"Received leaderboard data: {json_data}")

# Add new data to leaderboard
new_data = {
    "name": "New Person",
    "score": 20,
}

time.sleep(10)

socket.send(b"add_to_leaderboard")
response = socket.recv()
if response == b"ready":
    socket.send(convert_dict_to_bytes(new_data))
    response = socket.recv()
if response == b"added":
    print("Successfully added new score to leaderboard")
    time.sleep(5)
else:
    print("Failed to add")
