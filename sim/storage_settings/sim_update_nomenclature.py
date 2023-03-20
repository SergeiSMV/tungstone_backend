import ast
import json
import websockets
from router_init import router
from connections import sim_connect, sim_cursor


@router.route('/sim_update_nomenclature')
async def sim_update_nomenclature(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_sim_update_nomenclature(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass

async def f_sim_update_nomenclature(data):
    item_id = data['id']
    category = data['category']
    name = data['name']

    updt = 'UPDATE nomenclature SET category = %s, name = %s WHERE id = %s'
    updtValue = (category, name, item_id)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(updt, updtValue)
    sim_connect.commit()

    return 'done'