from server import sio

sid_to_user = {}

@sio.event
def join_room(sid, data):
    user = data["user"]
    room_name = data["room"]

    # Leave all rooms except the private room named after the sid
    rooms = sio.rooms(sid)
    for room in rooms:
        if room != sid:
            sio.leave_room(sid, room)

    # Get current participants in the target room
    participants = sio.manager.rooms["/"].get(data["room"], set())
    # Determine if the joining user will be the host (first in room)
    is_host = (len(participants) == 0)

    # Enforce maximum room size of 4 players
    if len(participants) >= 4:
        # Notify the joining client that the room is full
        sio.emit("join_failed", {"error": "Room is full"}, to=sid)
        return
    else:
        # Add the user to the room
        sio.enter_room(sid, data["room"])

        # Map the socket ID to the username for tracking
        sid_to_user[sid] = user

        # Confirm successful join only to the joining client
        sio.emit("join_success", {
            "user": user,
            "room": room_name,
            "ishost": is_host
        }, to=sid)

        # Notify all other clients in the room about the new player
        sio.emit("player_joined", {
            "user": user,
            "room": room_name
        }, room=data["room"], skip_sid=sid)

@sio.event
def leave_room(sid, data):
    room_name = data["room"]
    user = data["user"]
    
    # Remove the user from all rooms except their private room
    rooms = sio.rooms(sid)
    for room in rooms:
        if room != sid:  # skip private room named after sid
            sio.leave_room(sid, room)
    # Remove the user from the sid-to-user mapping
    sid_to_user.pop(sid, None)
    
    # Notify remaining clients in the room that the player has left
    sio.emit("player_left", {
        "user": user,
        "room": room_name
    }, room=room_name, skip_sid=sid)

    # Check if there are still participants in the room
    participants = sio.manager.rooms["/"].get(room_name, set())
    if participants:  # if room is not empty
        # Assign a new host (first participant in the set)
        new_host_sid = next(iter(participants))
        new_host_user = sid_to_user.get(new_host_sid, "Unknown")
        # Notify the room about the host change
        sio.emit("host_changed", {
            "new_host_sid": new_host_sid,
            "new_host_user": new_host_user
        }, room=room_name)
