from Chat.app import app,socketio
from Chat import event
if __name__ == '__main__':
    socketio.run(app,debug=True,log_output=True)