import os
from app.api import stocks
from app.api.models import db
from flask import request, current_app, abort
from app.api.models.stock import Stock, stocks_schema, stock_schema
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


STOCK_FILE_FOLDER = os.environ.get('STOCK_FOLDER')


@stocks.route('/stocks/upload', methods=['POST'])
@token_required
def upload_stock(user):
    """
    upload new batch stock for 
    saving into the database 
    this will be procurement department
    """
    receivedFile = request.files["newStockFile"]
    if receivedFile and allowed_file(receivedFile.filename):
        secureFilename = secure_filename(receivedFile.filename)
        filePath = os.path.join(
            current_app.root_path, STOCK_FILE_FOLDER, secureFilename)
        receivedFile.save(filePath)
        csvFile = convert_to_csv(filePath, STOCK_FILE_FOLDER)
        action_id = generate_id()
        # add item sys id and action id to csv
        add_item_sys_id(csvFile, action_id)
        # save action to db
        save_action_to_db(action_id, "Adding Stock", user['user_sys_id'])
        # save stock csv to db
        save_csv_to_db(csvFile, "public.'Stock'")
    return custom_make_response(
        "error",
        "Only excel files are allowed, select an excel file & try again.",
        400
    )


@stocks.route('/stocks', methods=['GET'])
@token_required
def get_all_stock(user):
    """ get all stock items """
    try:
        items = Stock.query.all()
        serialized_items = stocks_schema.dump(items)

        if not items:
            abort(
                404,
                "You don't have any stock items, add some and try again."
            )
        return custom_make_response("data", serialized_items, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


# this method might not be necessary since all
# stock items are prefetched and hence on the frontend
# items will be returned from a list and if it is not
# on the list then it is not on the database
# or we can check the list on the frontend and if not
# found then we check the db so it might stay
@stocks.route('/stocks/<id>', methods=['GET'])
def get_an_item(user, id):
    """ get a particular stock item """
    try:
        item = Stock.query.filter_by(item_sys_id=id).first()
        serialized_item = stock_schema.dump(item)

        if not item:
            abort(
                404,
                "You don't have the item in stock, add it and try again."
            )
        return custom_make_response("data", serialized_item, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@stocks.route('/stocks/<id>', methods=['PATCH'])
@token_required
def update_stock(user, id):
    """
    make changes to stock items
    """
    try:
        stock_to_update = request.get_json()
        item = Stock.query.filter_by(item_sys_id=id).first()
        serialized_item = stock_schema.dump(item)
        if not item:
            abort(
                404,
                "The stock item you want to make changes to does exist."
            )

        action_id = generate_id()
        item_to_update = serialized_item['item']
        save_action_to_db(
            action_id, f"Updated {item_to_update}", user['user_sys_id'])

        Stock.query.filter_by(item_sys_id=id).update(stock_to_update)
        db.session.commit()

        return custom_make_response(
            "data",
            f"{item_to_update} update successful.",
            200
        )

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@stocks.route('/stocks/<id>', methods=['DELETE'])
@token_required
def remove_stock_item(user, id):
    """
    remove stock items completely from the database
    """
    try:
        item = Stock.query.filter_by(item_sys_id=id).first()
        serialized_item = stock_schema.dump(item)

        if not item:
            abort(
                404,
                "The stock item you are deleting does exist."
            )

        action_id = generate_id()
        item_deleted = serialized_item['item']
        save_action_to_db(
            action_id, f"Removed {item_deleted}", user['user_sys_id'])

        Stock.query.filter_by(item_sys_id=id).delete()
        db.session.commit()
        return custom_make_response(
            "data",
            f"{item_deleted}  successfully removed from stock.",
            200
        )

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)
