import ast
import json
import websockets
from router_init import router
from connections import sim_connect, sim_cursor
from sim.sim_all_items import f_sim_all_items


@router.route('/sim_delete_item')
async def sim_delete_item(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_sim_delete_item(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_sim_delete_item(data):
    item_id = data['itemId']

    sql = 'DELETE FROM items WHERE id = %s'
    val = (item_id,)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sql, val)
    sim_cursor.fetchall()
    sim_connect.commit()

    sql = 'DELETE FROM history WHERE item_id = %s'
    val = (item_id,)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sql, val)
    sim_cursor.fetchall()
    sim_connect.commit()

    await f_sim_all_items(broadcast=True)
    return 'done'
