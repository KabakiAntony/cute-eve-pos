from app.api.models import db, ma
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    this is the user model
    """
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_sys_id = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    isActive = db.Column(db.Boolean, default=False)

    def __init__(self, user_sys_id, email, password, role):
        self.user_sys_id = user_sys_id
        self.email = email
        self.password = self.hash_password(password)
        self.role = role

    def hash_password(self, password):
        """
        given a password string of any form or size
        hash it in preparation for storage
        """
        password_hash = generate_password_hash(str(password))
        return password_hash

    def compare_password(hashed_password, password):
        """
        given a plain string password generate a hash
        that will be used to compare with the stored
        password in the database
        """
        return check_password_hash(hashed_password, str(password))



class UserSchema(ma.Schema):
    class Meta:
        fields = ("user_sys_id", "email", "password", "role", "isActive")


user_schema = UserSchema()
users_schema = UserSchema(many=True)

