from app.api.models import db, ma


class Item(db.Model):
    """
    Stock items model
    """
    __tablename__ = "Item"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_sys_id = db.Column(db.String(25), unique=True, nullable=False)
    action_id = db.Column(db.String(25), db.ForeignKey('Action.action_sys_id'))
    item = db.Column(db.String(255), unique=True, nullable=False)
    units = db.Column(db.Numeric, nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    children = db.relationship("Sale")

    def __init__(self, item_syd, action_id, item, units, bp, sp):
        self.item_sys_id = item_syd
        self.action_id = action_id
        self.item = item
        self.units = units
        self.buying_price = bp
        self.selling_price = sp


class ItemSchema(ma.Schema):
    class Meta:
        fields = (
            "item_sys_id", "action_id", "item", "units", 
            "buying_price", "selling_price")


item_schema = ItemSchema()
items_schema = ItemSchema(many=True)
