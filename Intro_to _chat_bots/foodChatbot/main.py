from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }

    return intent_handler_dict[intent](parameters, session_id)


def add_to_order(parameters: dict, session_id):
    food_items = parameters['food-item']
    quantities = parameters['number']

    if len(food_items) != len(quantities):
        fulfillmentText = "Sorry I didn't understand. Please specify food items and quantities."
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
           current_food_dict = inprogress_orders[session_id]
           # current_food_dict.update(new_food_dict)
           # Increment quantities for existing items
           for item, quantity in new_food_dict.items():
               current_food_dict[item] = current_food_dict.get(item, 0) + quantity

           inprogress_orders[session_id] = current_food_dict

        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillmentText = f"Your order so far is: {order_str}. Do you need anything else?"

    return JSONResponse(content={
        'fulfillmentText': fulfillmentText
    })


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillmentText = "Sorry, I'm having trouble finding your order. Could you place a new order?"
    elif len(inprogress_orders[session_id]) == 0:
        fulfillmentText = f"You have not ordered anything. Type 'New order' to make a new order"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillmentText = "Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order"
        else:
            order_total = db_helper.get_total_order_price(order_id)
            # if order_total <= 0:
            #     db_helper.delete_order(order_id)
            #     fulfillmentText = f"You have not ordered anything. Type 'New order' to make a new order"

            fulfillmentText = f"Awesome. We have placed your order. " \
                               f"Here is your order id # {order_id}. " \
                               f"Your order total is {order_total} which you can pay at the time of delivery."

            del inprogress_orders[session_id]

    return JSONResponse(content={
        'fulfillmentText': fulfillmentText
    })


def save_to_db(order):
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
       rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

       if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, 'in progress')

    return next_order_id


def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillmentText = "Sorry, I'm having trouble finding your order. Could you place a new order?"

    current_order = inprogress_orders[session_id]
    food_items = parameters['food-item']
    quantities = parameters.get('number', [1] * len(food_items))  # Default to removing 1 quantity if not specified
    quantities = quantities if isinstance(quantities, list) else [quantities]

    removed_items = []
    no_such_items = []

    for item, quantity_to_remove in zip(food_items, quantities):
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            # print(type(current_order[item]), type(quantity_to_remove))
            if current_order[item] > 1 and current_order[item] > quantity_to_remove:
                current_order[item] -= quantity_to_remove
            else:
                del current_order[item]

    fulfillmentText = ''

    if len(removed_items) > 0:
        fulfillmentText += f'Removed {",".join(removed_items)} from your order.'
    if len(no_such_items) > 0:
        fulfillmentText += f' Your current order does not have {",".join(no_such_items)}.'

    if len(current_order) == 0:
        fulfillmentText += ' Your order is empty.'
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillmentText += f' Here is what is left of your order: {order_str}.'

    return JSONResponse(content={
        'fulfillmentText': fulfillmentText
    })


def track_order(parameters: dict, session_id):
    order_id = int(parameters['number'])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillmentText = f'The order status for order id {order_id} is: {order_status}'
    else:
        fulfillmentText = f'No order found with order id {order_id}'

    return JSONResponse(content={
        'fulfillmentText': fulfillmentText
    })