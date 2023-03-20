import ast
import json
import websockets
from router_init import router
from connections import sim_connect, sim_cursor
from sim.sql_functions.get_color_values import get_color_values
from sim.sql_functions.get_name_values import get_name_values
from sim.sql_functions.get_producer_values import get_producer_values
from sim.sql_functions.get_unit_values import get_unit_values


@router.route('/sim_get_barcode_item')
async def sim_get_barcode_item(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_sim_get_barcode_item(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_sim_get_barcode_item(data):
    barcode = data['barcode']

    sql = 'SELECT * FROM barcodes  WHERE barcode = %s'
    val = (barcode,)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sql, val)
    result = sim_cursor.fetchone()
    sim_connect.commit()

    name_values = await get_name_values(result['name'])

    category = name_values['category']
    name = name_values['name']
    color = '' if result['color'] == 0 else await get_color_values(result['color'])
    producer = await get_producer_values(result['producer'])
    unit = await get_unit_values(result['unit'])

    barcode_item = {
        'category': category,
        'name': name,
        'color': color,
        'producer': producer,
        'unit': unit
    }

    return barcode_item


