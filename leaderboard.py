# Microservice implementation
# CS361 Summer 2023 Assignment 9
# Michael Wendland

import zmq
import time
import json


def write_leaderboard(leaderboard_dict):
    """Write leaderboard dict to json file"""
    with open("./leaderboard/leaderboard.json", "w") as outfile:
        outfile.write(json.dumps(leaderboard_dict))


def get_leaderboard(return_dict=False):
    """Get current leaderboard and return as either dict or bytes"""
    with open('./leaderboard/leaderboard.json', 'r') as f:
        # Read from json file
        # Return either the dict or the bytes depending on argument
        if return_dict:
            return json.load(f)
        else:
            leaderboard_data = str(json.load(f))
    return leaderboard_data.encode()


def add_score(new_score):
    """Add new high score to leaderboard"""
    formatted_data = new_score.decode('utf-8')
    formatted_data = formatted_data.replace("\'", "\"")
    formatted_data = json.loads(formatted_data)
    leaderboard = get_leaderboard(return_dict=True)
    leaderboard["leaderboard"].append(formatted_data)
    write_leaderboard(leaderboard)


# Start socket
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8888")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received request: {message}")

    if message == b"get_leaderboard":
        leaderboard = get_leaderboard()
        socket.send(leaderboard)
    elif message == b"add_to_leaderboard":
        socket.send(b"ready")
        new_data = socket.recv()
        print(f"Preparing to add {new_data} to leaderboard")
        add_score(new_data)
        time.sleep(5)
        socket.send(b"added")

    time.sleep(5)
