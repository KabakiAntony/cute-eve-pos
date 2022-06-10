from app.api.models import db, ma


class Action(db.Model):
    """ various actions model for logging and other uses"""
    __tablename__ = "Action"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_sys_id = db.Column(db.String(25), unique=True, nullable=False)
    action = db.Column(db.String(255),  nullable=False)
    action_date = db.Column(db.Date, nullable=False)
    by = db.Column(db.String(25), db.ForeignKey('User.user_sys_id'))

    def __init__(self, action_sys_id, action, action_date, action_by):
        self.action_sys_id = action_sys_id
        self.action = action
        self.action_date = action_date
        self.by = action_by


class ActionSchema(ma.Schema):
    class Meta:
        fields = (
            "action_sys_id", "action",
            "action_date", "by"
        )


actionSchema = ActionSchema()
actions_schema = ActionSchema(many=True)

