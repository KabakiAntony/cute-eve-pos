from app.api import sales
from app.api.models import db
from flask import request, abort
from app.api.models.sale import Sale
from app.api.models.action import Action
from app.api.models.stock import Stock, stock_schema
from app.api.utils import (
    custom_make_response,
    token_required,
    generate_id,
    save_action_to_db
)


@sales.routes('/sales/record', methods=['POST'])
@token_required
def save_sale(user):
    """ record a particular sale into the database """
    try:
        sale = request.get_json()
        if len(sale) == 0:
            abort(400, "Sale data has not been saved well, try again.")

        action_id = generate_id()
        save_action_to_db(action_id, "Sale", user['user_sys_id'])

        # extract individual dicts
        # add a sales id and insert
        # them into the sales table
        for i in range(len(sale)):
            sale[i].update({'sale_id': f'{action_id}'})

            item_id = sale[i].item_id
            units = sale[i].units

            # this could be a source of an error
            # but for now it just stays as is
            new_sale = Sale(sale[i])
            db.session.add(new_sale)
            db.session.commit()

            update_stock(item_id, units)
            
        return custom_make_response(
            "data",
            "Sale recorded successfully", 200)

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)


@sales.routes('/sales/<user_id>', methods=['GET'])
@token_required
def get_particular_sale(user, user_id):
    """return sales by a particular person given their user_sys_id """
    try:
        sale_data = (
            db.session.query(Sale, Action, Stock)
            .filter(Sale.sale_id == Action.action_sys_id)
            .filter(Sale.item_id == Stock.item_id)
            .filter_by(by=user['user_sys_id'])
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


@sales.routes('/sales/<start_date>/<end_date>', method=['GET'])
@token_required
def get_sales_by_date(user, startDate, endDate):
    """ return sales given  start and end dates """
    try:
        sale_data = (
            db.session.query(Sale, Action, Stock)
            .filter(Sale.sale_id == Action.action_sys_id)
            .filter(Sale.item_id == Stock.item_id)
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


def update_stock(item_id, units_sold):
    """ Update stocks after sale """
    try:
        item = Stock.query.filter_by(item_sys_id=item_id).first()
        serialized_item = stock_schema.dump(item)

        units = serialized_item['units']
        new_units = units - units_sold

        Stock.query.filter_by(item_sys_id=item_id).update(
            dict(quantity=new_units)
        )
        db.session.commit()

    except Exception as e:
        return custom_make_response("error", f"{str(e)}", e.code)
