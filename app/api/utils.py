import os
import re
import jwt
import random
import string
from functools import wraps
from flask import jsonify, make_response, abort, request
from app.api.models.users import Users, user_schema
from jwt import DecodeError, ExpiredSignatureError


KEY = os.getenv("SECRET_KEY")


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
            current_user = Users.query.filter_by(user_sys_id=data['id']).first()
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