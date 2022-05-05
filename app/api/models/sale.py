import datetime
from app.api.models import db, ma


class Sales(db.Model):
    """sales model"""
    __tablename__ = "Sales"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(db.Integer, db.ForeignKey('Stocks.id'))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Numeric, nullable=False)
    sold_by = db.Column(db.String(25), db.ForeignKey('Users.user_sys_id'))
    total = db.Column(db.Float, nullable=False)
    sale_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, item_id, price, quantity, sold_by, total):
        self.item_id = item_id
        self.price = price
        self.quantity = quantity
        self.sold_by = sold_by
        self.total = total


class SalesSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "item_id",
            "price", "quantity",
            "sold_by", "total",
            "sale_time"
        )


sale_schema = SalesSchema()
sales_schema = SalesSchema(many=True)
