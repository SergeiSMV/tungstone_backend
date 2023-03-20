import ast
import json
import websockets
from connections import sim_connect, sim_cursor
from router_init import router
import os

from sim.sql_functions.get_color_values import get_color_values
from sim.sql_functions.get_name_values import get_name_values
from sim.sql_functions.get_producer_values import get_producer_values
from sim.sql_functions.get_unit_values import get_unit_values

CLIENTS_SIM = {}


@router.route('/vk_all_items')
async def vk_all_items(ws, path):
    global CLIENTS_SIM
    user_id = 0
    try:
        while True:
            try:
                message = await ws.recv()
                client_data = ast.literal_eval(message)
                user_id = client_data['user_id']
                CLIENTS_SIM[user_id] = ws
                result = await f_vk_all_items()
                await ws.send(json.dumps(result))
                await ws.wait_closed()
            except websockets.ConnectionClosedOK:
                await delClient(user_id)
                break
    except websockets.ConnectionClosedError:
        await delClient(user_id)


async def f_vk_all_items(broadcast=False):
    allVkItemsList = []

    sql = 'SELECT * FROM vk_items'
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sql, )
    result = sim_cursor.fetchall()
    sim_connect.commit()

    for items in result:
        name_values = await get_name_values(items['name'])

        itemId = items['id']
        category = name_values['category']
        name = name_values['name']
        color = '' if items['color'] == 0 else await get_color_values(items['color'])
        producer = await get_producer_values(items['producer'])
        quantity = items['quant']
        unit = await get_unit_values(items['unit'])
        fifo = items['fifo'].strftime('%d.%m.%Y')
        author = items['author']

        items_map = {
            'itemId': itemId, 'category': category, 'name': name, 'color': color,
            'producer': producer, 'quantity': quantity, 'unit': unit, 'fifo': fifo,
            'author': author,
        }
        allVkItemsList.append(items_map)

    if broadcast:
        for ws in CLIENTS_SIM:
            await CLIENTS_SIM[ws].send(json.dumps(allVkItemsList))
    else:
        return allVkItemsList


async def delClient(user_id):
    try:
        del CLIENTS_SIM[user_id]
    except KeyError:
        pass
