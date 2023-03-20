import ast
import json
from datetime import datetime

import websockets
from router_init import router
from connections import sim_connect, sim_cursor
from sim.sql_functions.get_color_id import get_color_id
from sim.sql_functions.get_name_id import get_name_id
from sim.sql_functions.get_place_id import get_place_id
from sim.sql_functions.get_producer_id import get_producer_id
from sim.sql_functions.get_unit_id import get_unit_id

from sim.vk.vk_all_items import f_vk_all_items


@router.route('/vk_item_move')
async def vk_item_move(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_vk_item_move(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_vk_item_move(data):
    category = data['item']['category']
    name = data['item']['name']
    color = data['item']['color']
    producer = data['item']['producer']
    unit = data['item']['unit']

    date = data['item']['fifo']

    place = data['storage']
    cell = data['cell']
    total_quantity = data['total_quantity']

    item_id = data['item']['itemId']
    place_id = await get_place_id(place, cell)
    name_id = await get_name_id(category, name)
    color_id = 0 if color == '' else await get_color_id(color)
    producer_id = await get_producer_id(producer)
    quantity_move = data['quantity_move']
    unit_id = await get_unit_id(unit)
    fifo = datetime.strptime(date, '%d.%m.%Y').date()
    author = data['item']['author']

    sim = 'INSERT INTO items (place, name, color, producer, quant, unit, fifo, author) ' \
          'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    sim_val = (place_id, name_id, color_id, producer_id, quantity_move, unit_id, fifo, author)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sim, sim_val)
    sim_cursor.fetchall()
    sim_connect.commit()

    if int(quantity_move) == int(total_quantity):
        delete = 'DELETE FROM vk_items WHERE id = %s'
        delete_val = (item_id,)
        sim_connect.ping(reconnect=True)
        sim_cursor.execute(delete, delete_val)
        sim_cursor.fetchall()
        sim_connect.commit()
    else:
        update = 'UPDATE vk_items SET quant = %s - %s WHERE id = %s'
        update_val = (total_quantity, quantity_move, item_id)
        sim_connect.ping(reconnect=True)
        sim_cursor.execute(update, update_val)
        sim_cursor.fetchall()
        sim_connect.commit()

    await f_vk_all_items(broadcast=True)
    return 'done'
