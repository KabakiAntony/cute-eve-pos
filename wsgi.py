from app import create_app
from flask import render_template


app = create_app()

@app.route('/')
def root():
    """ defining the root of our app"""

    return "welcome to cute eve pos"


if __name__ == "__main__":
    app.run()