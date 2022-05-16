from app.api.models import db, ma


class Stock(db.Model):
    """
    Stocks model
    """
    __tablename__ = "stock"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_sys_id = db.Column(db.String(25), unique=True, nullable=False)
    action_id = db.Column(db.String(25), db.ForeignKey('Action.action_sys_id'))
    item = db.Column(db.String(255), unique=True, nullable=False)
    quantity = db.Column(db.Numeric, nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)

    def __init__(self, item_syd, action_id, item, qty, bp, sp):
        self.item_sys_id = item_syd
        self.action_id = action_id
        self.item = item
        self.quantity = qty
        self.buying_price = bp
        self.selling_price = sp


class StockSchema(ma.Schema):
    class Meta:
        fields = (
            "item_sys_id", "action_id", "item", "quantity", 
            "buying_price", "selling_price")


stock_schema = StockSchema()
stocks_schema = StockSchema(many=True)
