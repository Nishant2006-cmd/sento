from flask import Flask, render_template, redirect, request
from pymongo import MongoClient
from flask_socketio import SocketIO, join_room
import random
import string


app = Flask(__name__)
socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


client = MongoClient(
    "mongodb+srv://admin:kuchbhi@cluster0.e70rphc.mongodb.net/watchparty?retryWrites=true&w=majority"
)

db = client["watchparty"]
rooms = db["rooms"]


def generate_room():

    while True:

        room = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        if rooms.find_one({"roomId": room}) is None:
            rooms.insert_one({
                "roomId": room
            })
            return room



@app.route("/")
def home():
    return render_template("index.html")



@app.route("/create")
def create():

    room = generate_room()

    username = request.args.get("username")

    return redirect(
        f"/chat/{room}?username={username}"
    )


@app.route("/chat/<room_id>")
def chat(room_id):

    username = request.args.get("username")

    return render_template(
        "chat.html",
        room=room_id,
        username=username
    )


@socketio.on("join")
def handle_join(data):

    print("==========")
    print("JOIN RECEIVED")
    print(data)
    print("==========")

    join_room(data["room"])

    socketio.emit(
        "message",
        {
            "username":"System",
            "message":data["username"]+" joined"
        },
        room=data["room"]
    )




@socketio.on("change_video")
def handle_change_video(data):

    socketio.emit(
        "video_changed",
        {
            "url": data["url"]
        },
        room=data["room"]
    )



@socketio.on("video:play")
def handle_play(data):
    socketio.emit("video:play", data, room=data["room"], include_self=False)

@socketio.on("video:pause")
def handle_pause(data):
    socketio.emit("video:pause", data, room=data["room"], include_self=False)

@socketio.on("video:seek")
def handle_seek(data):
    socketio.emit("video:seek", data, room=data["room"], include_self=False)



@socketio.on("send_message")
def send_message(data):

    print("MESSAGE RECEIVED:", data)

    socketio.emit(
        "message",
        data,
        room=data["room"]
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))

    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False
    )