from server import sio

sid_to_user = {}

team_state = {}


@sio.event
def choose_role(sid, data):
    user = data["user"]
    team = data["team"]
    role = data["role"]
    room = data["room"]
    get_room = team_state.get(room, "Unknown")
    if get_room == "Unknown":
        team_state[room] = {}
    get_team = team_state[room].get(team, "Unknown")
    if get_team == "Unknown":
        team_state[room][team] = {"giver": None, "guesser": None}
    if team_state[room][team][role] == None:
        team_state[room][team][role] = user
        sio.emit("update_roles", team_state[room], room=room)
    else:
        sio.emit("failed_update_roles", team_state[room], room=room)

@sio.event
def start_game(sid, data):
    room = data["room"]

    if len(team_state[room]) == 2 and all(
    role_value is not None
    for team in team_state[room].values()
    for role_value in team.values()
    ):
        sio.emit("start_game", None, room=room)

@sio.event
def random_player(sid, data):
    pass

@sio.event
def new_round(sid, data):
    # server announces new round
    pass

@sio.event
def submit_hint(sid, data):
    # clue giver submits hint
    pass

@sio.event
def submit_guess(sid, data):
    # guesser submits guess
    pass

@sio.event
def round_result(sid, data):
    # broadcast round result
    pass

@sio.event
def game_over(sid, data):
    # announce winner
    pass
