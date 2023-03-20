import ast
import json
import websockets
from router_init import router
from connections import sim_connect, sim_cursor
from sim.orders.sim_all_orders import f_sim_all_orders
from sim.orders.sim_order_items import f_sim_order_items
from sim.orders.sim_uniq_items import f_sim_uniq_items
from sim.sim_all_items import f_sim_all_items


@router.route('/sim_accept_extradition')
async def sim_accept_extradition(ws, path):
    try:
        try:
            message = await ws.recv()
            client_data = ast.literal_eval(message)
            result = await f_sim_accept_extradition(client_data)
            await ws.send(json.dumps(result))
        except websockets.ConnectionClosedOK:
            pass
    finally:
        pass


async def f_sim_accept_extradition(data):
    item_id = data['data']['item_id']
    fact_quantity = data['data']['fact_quant']
    num = data['data']['num']
    reserve_quantity = data['data']['quantity']

    edit_order = 'UPDATE orders SET status = 3 WHERE item_id = %s'
    order_value = (item_id, )
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(edit_order, order_value)
    sim_connect.commit()

    edit_sim = 'UPDATE items SET quant = quant - %s, reserve = reserve - %s WHERE id = %s'
    sim_value = (fact_quantity, reserve_quantity, item_id)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(edit_sim, sim_value)
    sim_connect.commit()

    await f_sim_all_orders(broadcast=True)
    await f_sim_order_items(num, broadcast=True)
    await f_sim_all_items(broadcast=True)
    await f_sim_uniq_items(broadcast=True)

    return 'done'
