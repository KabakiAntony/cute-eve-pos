from flask import Blueprint


users = Blueprint("users", __name__, url_prefix="")
stocks = Blueprint("stocks", __name__, url_prefix="")
sales = Blueprint("sales", __name__, url_prefix="")