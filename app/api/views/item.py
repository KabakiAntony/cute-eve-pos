import os
from app.api import items
from app.api.models import db
# remove this import once done
from sqlalchemy import create_engine
from psycopg2.errors import (
    UniqueViolation,
    InvalidTextRepresentation,
    BadCopyFileFormat
 ) 
from flask import request, current_app, abort
from app.api.models.item import Item, items_schema, item_schema
from werkzeug.utils import secure_filename
from app.api.utils import (
    allowed_file,
    custom_make_response,
    token_required,
    convert_to_csv,
    add_item_sys_id,
    generate_id,
    save_csv_to_db,
    save_action_to_db
)


ITEM_FILE_FOLDER = os.environ.get('ITEM_FOLDER')
RESTORE_FILE_FOLDER = os.environ.get('RESTORE_FOLDER')
DB_URL = os.environ.get("DATABASE_URL").replace(
    'postgres://', 'postgresql://')


@items.route('/items/upload', methods=['POST'])
@token_required
def upload_Item(user):
    """
    upload new batch Item for 
    saving into the database 
    this will be procurement department
    """
    receivedFile = request.files["newItemFile"]
    if receivedFile and allowed_file(receivedFile.filename):
        secureFilename = secure_filename(receivedFile.filename)
        filePath = os.path.join(
            current_app.root_path, ITEM_FILE_FOLDER, secureFilename)
        receivedFile.save(filePath)
        csvFile = convert_to_csv(filePath, ITEM_FILE_FOLDER)
        action_id = generate_id()
        # add item sys id and action id to csv
        add_item_sys_id(csvFile, action_id)

        try:
            # save action to db
            save_action_to_db(action_id, "Adding new items", user['user_sys_id'])

            # save Item csv to db
            save_csv_to_db(csvFile, 'public."Item"')

            return custom_make_response(
                "data",
                "File uploaded successfully and  items saved to database.",
                200
            )
        except UniqueViolation:
            db.session.rollback()
            return custom_make_response(
                "error",
                "Some of the items you are adding already exist,\
                    remove them and try again.",
                400
            )
        except InvalidTextRepresentation:
            db.session.rollback()
            return custom_make_response(
                "error",
                "Some of the columns in your file are empty, \
                    check them and try again.",
                400
            )
        except BadCopyFileFormat:
            db.session.rollback()
            return custom_make_response(
                "error",
                "Some of the data in the item column\
                    contains commas remove them and try\
                        again",
                400
            )

    return custom_make_response(
        "error",
        "Only excel files are allowed, select an excel file & try again.",
        400
    )


@items.route('/items', methods=['GET'])
@token_required
def get_all_Item(user):
    """ get all Item items """
    try:
        items = Item.query.all()
        serialized_items = items_schema.dump(items)

        if not items:
            abort(
                404,
                "You don't have any Item items, add some and try again."
            )
        return custom_make_response("data", serialized_items, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


# this method might not be necessary since all
# Item items are prefetched and hence on the frontend
# items will be returned from a list and if it is not
# on the list then it is not on the database
# or we can check the list on the frontend and if not
# found then we check the db so it might stay
@items.route('/items/<id>', methods=['GET'])
@token_required
def get_an_item(user, id):
    """ get a particular Item item """
    try:
        item = Item.query.filter_by(item_sys_id=id).first()
        serialized_item = item_schema.dump(item)

        if not item:
            abort(
                404,
                "You don't have the item in Item, add it and try again."
            )
        return custom_make_response("data", serialized_item, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@items.route('/items/<id>', methods=['PATCH'])
@token_required
def update_Item(user, id):
    """
    make changes to Item items
    """
    try:
        item_to_update = request.get_json()
        item = Item.query.filter_by(item_sys_id=id).first()
        serialized_item = item_schema.dump(item)
        if not item:
            abort(
                404,
                "The Item item you want to make changes to does exist."
            )

        action_id = generate_id()

        save_action_to_db(
            action_id, f"Updated {serialized_item['item']}", user['user_sys_id'])

        # append action_id to item_to_update
        item_to_update['action_id'] = f"{action_id}"

        Item.query.filter_by(item_sys_id=id).update(item_to_update)
        db.session.commit()

        return custom_make_response(
            "data",
            f"{item_to_update['item']} updated successfully.",
            200
        )

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@items.route('/items/<id>', methods=['DELETE'])
@token_required
def remove_Item_item(user, id):
    """
    remove Item items completely from the database
    """
    try:
        item = Item.query.filter_by(item_sys_id=id).first()
        serialized_item = item_schema.dump(item)

        if not item:
            abort(
                404,
                "The Item item you are deleting does exist."
            )

        action_id = generate_id()
        item_deleted = serialized_item['item']
        save_action_to_db(
            action_id, f"Removed {item_deleted}", user['user_sys_id'])

        Item.query.filter_by(item_sys_id=id).delete()
        db.session.commit()
        return custom_make_response(
            "data",
            f"{item_deleted}  successfully removed from Item.",
            200
        )

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


# a method that will be used to restore all items on the database
# it will take csv files
@items.route('/restore', methods=['POST'])
def restore_data():
    """ restore all data into the database"""
    receivedFile = request.files["restoredCsv"]
    if receivedFile:
        secureFilename = secure_filename(receivedFile.filename)
        filePath = os.path.join(
            current_app.root_path, RESTORE_FILE_FOLDER, secureFilename)
        receivedFile.save(filePath)
    try:
        # restore data to the different tables and 
        # change this accordingly
        engine = create_engine(DB_URL)
        konnection = engine.raw_connection()
        kursor = konnection.cursor()
        with open(filePath, "r") as f:
            next(f)
            kursor.copy_expert(f"COPY public.'User'(user_sys_id,email,password,\
                role,isActive) FROM STDIN WITH DELIMITER','", f)
        konnection.commit()
    except Exception as e:
        print(e,"the following error occurred.")
        return custom_make_response("error", f"{str(e)}", e.code)
