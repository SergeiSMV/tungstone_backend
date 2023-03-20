import ast
import json
from datetime import datetime

import websockets
from router_init import router
from connections import sim_connect, sim_cursor
from sim.sim_all_items import f_sim_all_items
from sim.sql_functions.get_color_id import get_color_id
from sim.sql_functions.get_name_id import get_name_id
from sim.sql_functions.get_place_id import get_place_id
from sim.sql_functions.get_producer_id import get_producer_id
from sim.sql_functions.get_unit_id import get_unit_id


@router.route('/sim_add_item')
async def sim_add_item(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_sim_add_item(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_sim_add_item(data):
    category = data['category']
    name = data['name']
    color = data['color']
    producer = data['producer']
    unit = data['unit']
    place = data['storage']
    cell = data['cell']

    name_id = await get_name_id(category, name)
    color_id = 0 if color == '' else await get_color_id(color)
    producer_id = await get_producer_id(producer)
    barcode = data['barcode']
    quant = data['quantity']
    unit_id = await get_unit_id(unit)
    string_date = data['date']
    date = datetime.strptime(string_date, '%d.%m.%Y')
    author = data['author']

    if not place:
        add_to_vk = 'INSERT INTO vk_items (name, color, producer, quant, unit, fifo, author) ' \
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)'
        vk_value = (name_id, color_id, producer_id, quant, unit_id, date, author)
        sim_connect.ping(reconnect=True)
        sim_cursor.execute(add_to_vk, vk_value)
        sim_cursor.fetchall()
        sim_connect.commit()
    else:
        place_id = await get_place_id(place, cell)

        add_to_sim = 'INSERT INTO items (place, name, color, producer, quant, unit, fifo, author, status) ' \
                     'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        sim_value = (place_id, name_id, color_id, producer_id, quant, unit_id, date, author, 'work')
        sim_connect.ping(reconnect=True)
        sim_cursor.execute(add_to_sim, sim_value)
        sim_cursor.fetchall()
        sim_connect.commit()
        await f_sim_all_items(broadcast=True)

    if not barcode:
        pass
    else:
        barcodes = []

        check_barcode = 'SELECT * FROM barcodes'
        sim_connect.ping(reconnect=True)
        sim_cursor.execute(check_barcode, )
        result = sim_cursor.fetchall()
        sim_connect.commit()

        for b in result:
            barcodes.append(b['barcode'])

        if barcode in barcodes:
            pass
        else:
            add_to_bc = 'INSERT INTO barcodes (barcode, name, color, producer, unit) ' \
                        'VALUES (%s, %s, %s, %s, %s)'
            bc_value = (barcode, name_id, color_id, producer_id, unit_id)
            sim_connect.ping(reconnect=True)
            sim_cursor.execute(add_to_bc, bc_value)
            sim_cursor.fetchall()
            sim_connect.commit()

    return 'done'
