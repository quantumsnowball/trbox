from flask import Flask, render_template
from flask_socketio import SocketIO

from trbox.common.logger import Log, set_log_level

app = Flask(__name__)
socketio = SocketIO(app, logger=True)

set_log_level('INFO')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':

    Log.info('socketio.run()')
    socketio.run(app, host='localhost', port=5000)
