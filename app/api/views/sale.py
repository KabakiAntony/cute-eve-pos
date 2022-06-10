import datetime
from app.api import sales
from app.api.models import db
from flask import request, abort
from app.api.models.sale import Sale
from app.api.models.action import Action
from app.api.models.item import Item, item_schema
from app.api.utils import (
    custom_make_response,
    token_required,
    generate_id,
    save_action_to_db
)


@sales.route('/sales/record', methods=['POST'])
@token_required
def save_sale(user):
    """ record a particular sale into the database """
    try:
        sale = request.get_json()
        action_id = generate_id()
        save_action_to_db(action_id, "Sale", user['user_sys_id'])

        # extract individual dicts
        # add a sales id and insert
        # them into the sales table
        for i in range(len(sale)):
            item_id = sale[i]["item_sys_id"]
            unit_price = sale[i]["selling_price"]
            units = sale[i]["units"]
            total = sale[i]["total"]

            new_sale = Sale(
                sale_id=action_id,
                item_id=item_id,
                unit_price=unit_price,
                units=units,
                total=total
                )
            db.session.add(new_sale)
            db.session.commit()

            update_items(item_id, units)
            
        return custom_make_response(
            "data",
            "Sale recorded successfully", 201)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@sales.route('/sales', methods=['GET'])
@token_required
def get_particular_sale(user):
    """return sales by a particular person given their user_sys_id """
    try:
        start_date = datetime.datetime.now().strftime("%m/%d/%Y, 00:00:00")
        end_date = datetime.datetime.now().strftime("%m/%d/%Y, 23:59:59")
        sale_data = (
            db.session.query(Sale, Action, Item)
            .filter(Sale.sale_id == Action.action_sys_id)
            .filter(Sale.item_id == Item.item_sys_id)
            .filter(Action.by == user['user_sys_id'])
            .filter(Action.time.between(start_date, end_date))
            .all()
        )

        if not sale_data:
            abort(404, "No sale data has been found for the user.")

        sale_list = []
        for result in sale_data:
            # return all fields but we will
            # we will leave all relevant fields later
            result_format = {
                # "item_id": result[0].item_id,
                # "sale_id": result[0].sale_id,
                "unit_price": result[0].unit_price,
                "units_sold": float(result[0].units),
                "total": result[0].total,
                # "action_sys_id": result[1].action_sys_id,
                # "action": result[1].action,
                "time": result[1].time.strftime("%m/%d/%Y, %H:%M:%S"),
                # "by": result[1].by,
                # "item_sys_id": result[2].item_sys_id,
                # "action_id": result[2].action_id,
                "item": result[2].item,
                # "buying_price": result[2].buying_price,
                # "selling_price": result[2].selling_price,
            }
            sale_list.append(result_format)
        return custom_make_response("data", sale_list, 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@sales.route('/sales/<start_date>/<end_date>', methods=['GET'])
@token_required
def get_sales_by_date(user, startDate, endDate):
    """ return sales given  start and end dates """
    try:
        sale_data = (
            db.session.query(Sale, Action, Item)
            .filter(Sale.sale_id == Action.action_sys_id)
            .filter(Sale.item_id == Item.item_id)
            .filter(Action.time.between(f'{startDate}', f'{endDate}'))
        )

        if not sale_data:
            abort(404, "No sale data has been found for the user.")

        sale_list = []
        for result in sale_data:
            # return all fields but we will
            # we will leave all relevant fields later
            result_format = {
                "item_id": result[0].item_id,
                "sale_id": result[0].sale_id,
                "unit_price": result[0].unit_price,
                "units": result[0].units,
                "total": result[0].total,
                "action_sys_id": result[1].action_sys_id,
                "action": result[1].action,
                "time": result[1].time.strftime("%m/%d/%Y, %H:%M:%S"),
                "by": result[1].by,
                "item_sys_id": result[2].item_sys_id,
                "action_id": result[2].action_id,
                "item": result[2].item,
                "quantity": result[2].quantity,
                "buying_price": result[2].buying_price,
                "selling_price": result[2].selling_price,
            }
            sale_list.append(result_format)
        return custom_make_response("data", sale_list, 200)
        
    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


def update_items(item_id, units_sold):
    """ Update items after sale """
    try:
        item = Item.query.filter_by(item_sys_id=item_id).first()
        serialized_item = item_schema.dump(item)

        units = float(serialized_item['units'])
        new_units = units - units_sold

        Item.query.filter_by(item_sys_id=item_id).update(
            dict(units=new_units)
        )
        db.session.commit()

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)
