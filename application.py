#!/usr/bin/env python3
from flask import Flask

app = Flask(__name__)


@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello World"


if __name__ == '__main__':
    # TODO: remove debug mode
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
