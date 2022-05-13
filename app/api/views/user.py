import os
import jwt
import datetime
from app.api import users
from app.api.models import db
from flask import request, abort
from app.api.models.user import User, user_schema
from werkzeug.security import generate_password_hash
from app.api.utils import (
    generate_random_password,
    check_for_whitespace,
    custom_make_response,
    isValidPassword,
    isValidEmail,
    generate_id,
    token_required
)
from app.api.email_utils import (
    send_mail,
    email_signature,
    activate_email_content,
    button_style,
    password_reset_content
)


# get environment variables
KEY = os.getenv("SECRET_KEY")
ACTIVATE_ACCOUNT_URL = os.getenv("ACTIVATE_ACCOUNT_URL")
PASSWORD_RESET_URL = os.getenv("PASSWORD_RESET_URL")


@users.route('/users/create', methods=['POST'])
@token_required
def create_user(user):
    """
    and admin user is the one who will
    create accounts for the system users
    you cannot just signup.
    The admin account will be created first
    time this app is loaded and that is it.
    """
    if user['role'] != 'admin':
        abort(
            401,
            "You are not authorized to create system users.")

    try:
        user_data = request.get_json()

        if ('email' or 'password') not in user_data.keys():
            abort(
                400,
                """
                Email and or password is missing,
                please check and try again.
                """)

        email = user_data["email"]
        role = user_data["role"]
        password = generate_random_password()
        sys_gen_id = generate_id()

        check_for_whitespace(user_data, ["email", "password"])
        isValidEmail(email)
        isValidPassword(password)

        if User.query.filter_by(email=email).first():
            abort(
                409,
                """
                An account for that user already exists,
                have them reset their password if forgotten or
                send them a fresh account activation link.
                """
            )

        sys_gen_id = generate_id()
        new_user = User(
            user_sys_id=sys_gen_id, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        token = jwt.encode(
                {
                    "id": sys_gen_id,
                    "exp":
                    datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                },
                KEY,
                algorithm="HS256",
            )

        subject = """Activate your account."""
        content = f"""
        Hey {email.split('@', 1)[0]},
        {activate_email_content()}
        <a href="{ACTIVATE_ACCOUNT_URL}?tkn={token.decode('utf-8')}"
        style="{button_style()}">Activate account</a>
        {email_signature()}
        """
        send_mail(email, subject, content)

        return custom_make_response(
            "data",
            {
                "message":
                f"An account for {email.split('@', 1)[0]} has been created successfully\
                    and an activation link sent to their email.",
                # "tkn": token.decode('utf-8'),
            }, 201
        )

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@users.route('/users/login', methods=["POST"])
def user_signin():
    """
    Signin a user into the system.
    """
    try:
        user_data = request.get_json()

        if ('email' or 'password') not in user_data.keys():
            abort(
                400,
                """
                Email and or password is missing,
                please check and try again.""")

        email = user_data['email']
        password = user_data['password']

        check_for_whitespace(user_data, ["email", "password"])
        isValidEmail(email)
        isValidPassword(password)

        user = User.query.filter_by(email=email).first()
        if not user:
            abort(
                404,
                "An account has not been created for you, \
                have the admin to create one for you.")

        _user = user_schema.dump(user)
        _password = _user["password"]

        if not _user['isActive']:
            abort(
                401,
                """
                You have not activated your account, check for
                activation email in your inbox,
                or have the admin send you a new one.
                """)

        if not User.compare_password(_password, password):
            abort(
                403,
                "Email and or password is incorrect,\
                    please check and try again.")

        token = jwt.encode(
            {
                "id": _user["user_sys_id"],
                "role": _user['role'],
                "exp":
                datetime.datetime.utcnow() + datetime.timedelta(minutes=480),
            },
            KEY,
            algorithm="HS256",
        )
        response = custom_make_response(
            "data",
            {
                "message":
                "Signed in successfully preparing your dashboard...",
                "auth_token": token.decode('utf-8'),
                "screen_name": email.split('@', 1)[0],
            }, 200
        )
        return response

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@users.route('/users/forgot', methods=['POST'])
def forgot_password():
    """
    Send a password reset link when a user has
    forgotten their password on request.
    """
    try:
        user_data = request.get_json()

        if 'email' not in user_data.keys():
            abort(400, "Email is missing, please enter and try again.")

        email = user_data['email']

        check_for_whitespace(user_data, ["email"])
        isValidEmail(email)
        user = User.query.filter_by(email=user_data["email"]).first()
        this_user = user_schema.dump(user)

        if user:
            token = jwt.encode(
                {
                    "id": this_user["user_sys_id"],
                    "email": email,
                    "exp": datetime.datetime.utcnow() + datetime.
                    timedelta(minutes=30),
                },
                KEY,
                algorithm="HS256",
            )

            subject = """Password Reset Request"""
            content = f"""
            Hey {this_user['email'].split('@', 1)[0]},
            {password_reset_content()}
            <a href="{PASSWORD_RESET_URL}?tkn={token.decode('utf-8')}"
            style="{button_style()}"
            >Reset Password</a>
            {email_signature()}
            """
            send_mail(email, subject, content)

        response = custom_make_response(
            "data", {
                "message": "An email has been sent to the address on record,\
                If you don't receive one shortly, please contact\
                    the site admin.",
                # will see if this token is eventually needed or not.
                "tkn": token.decode('utf-8'),
            }, 202
        )
        return response

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@users.route('/users/update', methods=['PATCH'])
@token_required
def update_password(user):
    """
    Update or change the user password
    :param user: a user object will be passed on from
    the decoded token therefore you will be able to access
    various user attributes an id and email uniquely identifying
    the user and therefore updating their password accoringly
    """
    try:
        user_data = request.get_json()

        if ('email' or 'password') not in user_data.keys():
            abort(
               400,
               """
               Email and or password is missing,
               please check and try again.
               """)
        email = user['email']
        new_password = user_data['password']

        check_for_whitespace(user_data, ["email", "password"])
        isValidEmail(email)
        isValidPassword(new_password)

        User.query.filter_by(email=user["email"]).update(
            dict(password=f"{generate_password_hash(str(new_password))}")
        )
        db.session.commit()

        # add email sending on successful password change.
        return custom_make_response(
            "data",
            "Your password has been changed successfully.",
            200
        )
    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@users.route('/users/activate', methods=['PATCH'])
@token_required
def activate_user_account(user):
    """
    This activates user account by doing a number of things
    sets a new password for the user, sets isactive status to
    true for the user account and also ensures first and foremost
    that the user being registered into the system is using real email.
    """
    try:
        new_password = request.get_json()
        account_activation_data = {
            "password": generate_password_hash(str(new_password)),
            "isActive": True
        }
        User.query.filter_by(
            email=user["email"]).update(account_activation_data)
        db.session.commit()

        return custom_make_response(
            "data",
            """
            You have successfully activated your account, please
            hold on as we take you to the login page.
            """,
            200
        )
    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)
