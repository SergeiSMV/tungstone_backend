import ast
import json
import websockets
from router_init import router
from connections import sim_connect, sim_cursor
from sim.history.sim_create_history import sim_create_history

from sim.sim_all_items import f_sim_all_items
from sim.sql_functions.get_place_id import get_place_id


@router.route('/sim_item_move')
async def sim_item_move(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_sim_item_move(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_sim_item_move(data):
    item_id = data['itemId']
    new_place = data['storage']
    new_cell = data['cell']
    old_place = data['old_storage']
    old_cell = data['old_cell']
    author = data['author']
    comment = f'из: {old_place}: {old_cell}\nна: {new_place}: {new_cell}'

    # запись в историю
    await sim_create_history(item_id, 'перемещение', comment, author)

    place_id = await get_place_id(new_place, new_cell)

    sql = 'UPDATE items SET place = %s WHERE id = %s'
    val = (place_id, item_id)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sql, val)
    sim_cursor.fetchall()
    sim_connect.commit()

    await f_sim_all_items(broadcast=True)
    return 'done'
