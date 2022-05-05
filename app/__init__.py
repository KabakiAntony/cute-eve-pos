from flask import Flask


def create_app():
    """ initializing the app factory """
    app = Flask(__name__)

    return app