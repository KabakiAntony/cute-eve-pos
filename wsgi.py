from app import create_app

app = create_app()


@app.route('/')
def root():
    """
    this is the root of the api
    later on we need to create a
    root template for the api.
    """

    return "welcome to cute eve pos"


if __name__ == "__main__":
    app.run()