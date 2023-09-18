import sqlite3
def insert_into_table(columns, values, table_name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = "INSERT INTO %s (%s) VALUES (%s);" % (table_name, ','.join(columns), ','.join('?' * len(values)))
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()


def select_from_table(table_name, column_names, filters=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = "SELECT %s FROM %s" % (','.join(column_names), table_name)
    if filters:
        query += " " + filters

    cursor.execute(query)
    data = cursor.fetchall()

    result_list = []
    for row in data:
        row_dict = dict(zip(column_names, row))
        result_list.append(row_dict)
    
    cursor.close()
    conn.close()
    return result_list