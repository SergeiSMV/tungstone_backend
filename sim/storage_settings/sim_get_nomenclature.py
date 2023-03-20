import ast
import json
import websockets
from router_init import router
from connections import sim_connect, sim_cursor


@router.route('/sim_get_nomenclature')
async def sim_get_nomenclature(ws, path):
    try:
        try:
            result = await f_sim_get_nomenclature()
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_sim_get_nomenclature():

    sql = 'SELECT * FROM nomenclature'
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(sql, )
    result = sim_cursor.fetchall()
    sim_connect.commit()

    return result


