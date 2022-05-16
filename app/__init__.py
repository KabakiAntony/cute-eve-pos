from flask import Flask
from config import ProductionConfig
from flask_migrate import Migrate
from app.api.views.sale import sales as sales_blueprint
from app.api.views.stock import stocks as stocks_blueprint
from app.api.views.user import users as users_blueprint
from flask_cors import CORS


migrate = Migrate(compare_type=True)


def create_app():
    """ initializing the app factory """
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(ProductionConfig())

    from app.api.models import db, ma

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(sales_blueprint)
    app.register_blueprint(stocks_blueprint)
    app.register_blueprint(users_blueprint)
    app.app_context().push()

    return app