import ast
import json
import websockets
from router_init import router
from connections import sim_connect, sim_cursor


@router.route('/sim_create_nomenclature')
async def sim_create_nomenclature(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_sim_create_nomenclature(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_sim_create_nomenclature(data):
    category = data['category']
    name = data['name']

    add_nomenclature = 'INSERT INTO nomenclature (category, name) VALUES (%s, %s)'
    nomenclature_value = (category, name)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(add_nomenclature, nomenclature_value)
    sim_cursor.fetchall()
    sim_connect.commit()

    return 'done'
