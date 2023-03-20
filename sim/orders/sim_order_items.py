import ast
import json
import websockets
from connections import sim_connect, sim_cursor
from router_init import router
from sim.sql_functions.get_color_values import get_color_values
from sim.sql_functions.get_name_values import get_name_values
from sim.sql_functions.get_place_values import get_place_values
from sim.sql_functions.get_producer_values import get_producer_values
from sim.sql_functions.get_unit_values import get_unit_values

CLIENTS_SIM = {}


@router.route('/sim_order_items')
async def sim_order_items(ws, path):
    global CLIENTS_SIM
    user_id = 0
    try:
        while True:
            try:
                message = await ws.recv()
                client_data = ast.literal_eval(message)
                user_id = client_data['user_id']
                num = client_data['num']
                CLIENTS_SIM[user_id] = ws
                result = await f_sim_order_items(num)
                await ws.send(json.dumps(result))
                await ws.wait_closed()
            except websockets.ConnectionClosedOK:
                await delClient(user_id)
                break
    except websockets.ConnectionClosedError:
        await delClient(user_id)


async def f_sim_order_items(num, broadcast=False):
    orderItemsList = []

    sql = 'SELECT * FROM orders  WHERE num = %s'
    val = (num,)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sql, val)
    result = sim_cursor.fetchall()
    sim_connect.commit()

    for item in result:
        place_values = await get_place_values(item['place'])
        name_values = await get_name_values(item['name'])

        order_id = item['id']
        place = place_values['place']
        cell = place_values['cell']
        category = name_values['category']
        name = name_values['name']
        color = '' if item['color'] == 0 else await get_color_values(item['color'])
        producer = await get_producer_values(item['producer'])
        order_quant = item['order_quant']
        unit = await get_unit_values(item['unit'])
        status = item['status']
        comment = item['comment']
        item_id = item['item_id']
        fact_quant = item['fact_quant']

        items_map = {
            'order_id': order_id, 'place': place, 'cell': cell, 'category': category,
            'name': name, 'color': color, 'producer': producer, 'quantity': order_quant,
            'unit': unit, 'status': status, 'comment': comment, 'item_id': item_id, 'fact_quant': fact_quant,
            'num': num
        }
        orderItemsList.append(items_map)

    if broadcast:
        for ws in CLIENTS_SIM:
            await CLIENTS_SIM[ws].send(json.dumps(orderItemsList))
    else:
        return orderItemsList


async def delClient(user_id):
    try:
        del CLIENTS_SIM[user_id]
    except KeyError:
        pass
