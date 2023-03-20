from connections import sim_connect, sim_cursor


async def get_name_id(category, name):
    # получаем id категории и наименования
    name_sql = 'SELECT id FROM nomenclature WHERE category = %s AND name = %s'
    name_val = (category, name)
    sim_connect.ping(reconnect=True)
    sim_cursor.execute(name_sql, name_val)
    name_result = sim_cursor.fetchone()
    sim_connect.commit()

    name_id = name_result['id']
    return name_id
