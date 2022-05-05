from app.api.models import db, ma


class Users(db.Model):
    """
    this is the user model
    """
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_sys_id = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    isActive = db.Column(db.Boolean, default=False)

    def __init__(self, user_sys_id, email, password, role):
        self.user_sys_id = user_sys_id
        self.email = email
        self.password = password
        self.role = role


class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_sys_id", "email", "password", "role", "isActive")


userSchema = UserSchema()
usersSchema = UserSchema(many=True)

