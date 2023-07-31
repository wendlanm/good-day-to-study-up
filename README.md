**Communication contract:**

1.) Clear instructions for how to programmatically REQUEST data from the microservice (including example call).

To request data from the leaderboard microservice, set up a ZeroMQ client instance and send "get_leaderboard" formatted as bytes as shown below:

```
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:8888")
socket.send(b"get_leaderboard")
```

To request to ADD new data to the leaderboard, first send "add_to_leaderboard" formatted as bytes similar to what is shown above. Once "ready" is received from the microservice, then send the data as a Python dict data structure _encoded in UTF-8_:

```
new_data = {
    "name": "New Person",
    "score": 20,
}

socket.send(b"add_to_leaderboard")
response = socket.recv()
if response == b"ready":
    socket.send(str(new_data).encode())
    response = socket.recv()
```

2.) Clear instructions for how to programmatically RECEIVE data from the microservice you implemented.

To receive the leaderboard data, simply set up the ZeroMQ client as shown in part 1 and decode the data.

```
socket.send(b"get_leaderboard")
leaderboard_data = socket.recv()
leaderboard_data = leaderboard_data.decode('utf-8')
```

Note that the leaderboard_data will still be formatted as a string at this point. If you want to utilize the data as a dict, you will need to implement something like the following:

```
leaderboard_data = socket.recv()
leaderboard_data = leaderboard_data.decode('utf-8').replace("\'", "\"")
json_data = json.loads(leaderboard_data)
```

3.) UML sequence diagram showing how requesting and receiving data works. Make it detailed enough that your partner (and your grader) will understand.

<img width="306" alt="Screen Shot 2023-07-31 at 11 58 46 AM" src="https://github.com/wendlanm/good-day-to-study-up/assets/91234789/1abf0a1e-c248-408c-a25e-ec0f7d0d988f">

