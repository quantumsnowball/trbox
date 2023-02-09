from flask import Flask, render_template
from flask_socketio import SocketIO, send

from trbox.common.logger import Log, set_log_level

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

set_log_level('INFO')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(message):
    print(f'received message: {message}')
    send(message, broadcast=True)


if __name__ == '__main__':

    Log.info('socketio.run()')
    socketio.run(app, host='localhost', port=5000)
