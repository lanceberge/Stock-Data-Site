import sqlite3
def insert_into_database(data, table_name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    columns = ", ".join(data.keys())
    query = "INSERT INTO %s (%s) VALUES (%s);" % (table_name, columns, ','.join('?' * len(data.values())))
    cursor.execute(query, list(data.values()))
    conn.commit()
    cursor.close()
    conn.close()

