import datetime
from app.api.models import db, ma

class Stocksdb(db.Model):
    """
    Stocks model 
    """
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item = db.Column(db.String(255), unique=True, nullable=False)
    quantity = db.Column(db.Numeric, nullable=False)
    # buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.String(25), db.ForeignKey('Users.user_sys_id'))
    # updated_by = db.Column(db.String(25), db.ForeignKey('Users.user_sys_id'))

    def __init__(self, item, quantity, selling_price, created_by):
        self.item = item
        self.quantity = quantity
        # self.buying_price = buying_price
        self.selling_price = selling_price
        self.created_by = created_by
        # self.updated_by = updated_by


class StockSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "item", "quantity",
            "selling_price","creation_date", "update_date",
            "created_by")


stockSchema = StockSchema()
stocksSchema = StockSchema(many=True)
