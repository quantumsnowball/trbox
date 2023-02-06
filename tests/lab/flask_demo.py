from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "<p>Hello, World!</p>"


@app.route('/console')
def console():
    return "<p>Hello, World! Console.</p>"


if __name__ == '__main__':
    app.run(port=30000)
