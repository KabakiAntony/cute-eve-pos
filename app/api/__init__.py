from flask import Blueprint


users = Blueprint("users", __name__, url_prefix="")
items = Blueprint("items", __name__, url_prefix="")
sales = Blueprint("sales", __name__, url_prefix="")