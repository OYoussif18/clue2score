import socketio 

# Create Socket.IO server (shared instance)
sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp

# Import event handlers (they will use the same sio)
import rooms
import game_manager

if __name__ == "__main__":
    import eventlet
    eventlet.wsgi.server(eventlet.listen(("0.0.0.0", 5000)), app)
