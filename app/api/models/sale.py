from app.api.models import db, ma


class Sale(db.Model):
    """better sales model"""
    __tablename__ = "Sale_Two"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sale_id = db.Column(
        db.String(25),  db.ForeignKey('Action.action_sys_id'))
    item_id = db.Column(db.String(25), db.ForeignKey('Item.item_sys_id'))
    buying_price = db.Column(db.Float, nullable=False)
    units = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    def __init__(self, sale_id, item_id, buying_price, units, total):
        self.sale_id = sale_id
        self.item_id = item_id
        self.buying_price = buying_price
        self.units = units
        self.total = total


class SaleSchema(ma.Schema):
    class Meta:
        fields = (
            "item_id", "sale_id",
            "buying_price", "units", "total"
            )


sale_schema = SaleSchema()
sales_schema = SaleSchema(many=True)
