import os
import re
import jwt
import random
import string
import pandas
from datetime import datetime
from pytz import timezone
from pandas import read_excel
from sqlalchemy import create_engine
from functools import wraps
from flask import (
    jsonify,
    make_response,
    abort, request,
    current_app
)
from app.api.models import db
from app.api.models.user import User, user_schema
from app.api.models.action import Action
from jwt import DecodeError, ExpiredSignatureError


KEY = os.getenv("SECRET_KEY")
DB_URL = os.environ.get("DATABASE_URL").replace(
    'postgres://', 'postgresql://')
ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS')


def allowed_file(filename):
    """check for allowed extensions"""
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def custom_make_response(key, message, status):
    """
    This is a custom make response to make a
    json object that is returned by all endpoints
    :param key: this will make the key for the json object
    it will be either 'data or error'
    For successful actions the key will 'data' and for
    failures the key will be 'error'
    :param value: this will be the value for the above 'key'
    parameter
    :param status: this will be a status code for the return
    """
    raw_dict = {"status": status}
    if key == 'error' and ':' in message:
        message = message.split(':', 1)[1]
    raw_dict[key] = message
    return make_response(jsonify(raw_dict), status)


def isValidPassword(password):
    """
    Check if a password meets the requirements for a password
    :param password: is the password that is being checked
    """
    if len(password) < 8:
        abort(400, "Password should be atleast 8 characters")


def isValidEmail(email):
    """
    Check if an email is a valid email string,
    :param email: is the email string to be checked for validity
    """
    if not re.match(
            r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
        abort(400, "Please enter a valid email address")
    return True


def check_for_whitespace(data, items_to_check):
    """
    Check if the data supplied has whitespace and
    if the fields are empty, if the  fields are not
    empty strip the whitespace.
    :param data: this is a list holding key value pairs
    that are to be stripped for whitespace
    :param items_to_check: this are singular elements in the data
    """
    for key, value in data.items():
        if key in items_to_check and not value.strip():
            abort(
                400,
                "One or more of your fields is empty,\
                    please check and try again.")
    return True


def token_required(f):
    """
    Get a token from certain routes decode it
    for validity and correctness to acertain that
    the user who possesses it is who they are or is allowed to
    carryout the action that they want to carryout.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user_token = None

        if 'auth_token' not in request.headers:
            return custom_make_response(
                "error",
                "Token is missing, request one and try again.", 403)

        user_token = request.headers['auth_token']

        try:
            data = jwt.decode(user_token, KEY, algorithm="HS256")
            current_user = User.query.filter_by(
                user_sys_id=data['id']).first()
            _data = user_schema.dump(current_user)

        except ExpiredSignatureError:
            return custom_make_response(
                "error",
                "Token is expired, request a new one and try again.", 403)

        except DecodeError:
            return custom_make_response(
                "error",
                "The token is invalid, request a new one and try again.", 403)

        return f(_data, *args, **kwargs)
    return decorated


def generate_id():
    """
    generate a unique id for the system 
    not the primary key user_sys_id
    """
    id = string.ascii_letters + string.digits
    id = "".join(random.choice(id) for i in range(10))
    return id


def generate_random_password():
    """
    generate random password for users
    signed up by admin, it is not used
    anywhere by for maintaining data
    sanity in the db
    """
    random_source = string.ascii_letters + string.digits + string.punctuation
    password = random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)

    for i in range(8):
        password += random.choice(random_source)

    password_list = list(password)
    random.SystemRandom().shuffle(password_list)
    password = "".join(password_list)
    return password


def save_action_to_db(action_id, action, action_by):
    """
    this will be re used for all inserts or
    updates to make sure that each action on the
    system will be recorded on the action table
    for future use or review.
    """
    try:
        todays_date = africa_nairobi_date_now()
        new_action = Action(
            action_sys_id=action_id,
            action=action,
            action_date=todays_date,
            action_by=action_by)
        db.session.add(new_action)
        db.session.commit()
    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


def convert_to_csv(file_path, upload_dir):
    """convert excel file to csv"""
    dataFile = read_excel(file_path, engine="openpyxl")
    base_name = os.path.basename(file_path)
    csv_file_name = os.path.splitext(base_name)[0]
    new_upload_dir_path = os.path.join(current_app.root_path, upload_dir)
    csv_file_path = new_upload_dir_path + csv_file_name + ".csv"
    dataFile.to_csv(csv_file_path, index=False)
    return csv_file_path


def add_item_sys_id(csv_file, action_id):
    """ adding a unique system id for an item """
    data_file = pandas.read_csv(csv_file)
    rows = data_file.count()[0]
    data_file.insert(1, "item_sys_id", "")
    data_file.insert(2, "action_id", "")
    for row in range(rows):
        new_id = generate_id()
        data_file.loc[row, "item_sys_id"] = new_id
        data_file.loc[row, "action_id"] = action_id
        row + 1

    data_file.to_csv(csv_file, index=False)
    data_file = pandas.read_csv(csv_file)


def save_csv_to_db(csv_file, db_table):
    """
    Insert the contents of the csv file to
    the database table.
    """
    engine = create_engine(DB_URL)
    konnection = engine.raw_connection()
    kursor = konnection.cursor()
    with open(csv_file, "r") as f:
        next(f)
        kursor.copy_expert(f"COPY {db_table}(item,item_sys_id,action_id,\
            units,buying_price,selling_price) FROM STDIN WITH DELIMITER','", f)
    konnection.commit()


def africa_nairobi_date_now():
    """ this app needs to save dates in EAT"""
    # format = "%Y/%m/%d %H:%M:%S"

    now_utc = datetime.now(timezone('UTC'))

    now_nairobi = now_utc.astimezone(timezone('Africa/Nairobi'))

    now_nairobi_date = now_nairobi.date()
    return now_nairobi_date
