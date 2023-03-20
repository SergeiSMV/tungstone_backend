import pymysql.cursors

users_connect = pymysql.connect(host='localhost', port=3306, user='root', password='2001', db='r_users', cursorclass=pymysql.cursors.DictCursor)
users_cursor = users_connect.cursor()

sim_connect = pymysql.connect(host='localhost', port=3306, user='root', password='2001', db='r_sim', cursorclass=pymysql.cursors.DictCursor)
sim_cursor = sim_connect.cursor()
