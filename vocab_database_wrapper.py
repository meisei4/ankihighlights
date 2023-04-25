
def get_table_info(db_connection_injection):
    table_info = {}
    with db_connection_injection:
        cursor = db_connection_injection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            table_columns = {}
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                column_name = column[1]
                data_type = column[2]
                table_columns[column_name] = data_type

            table_info[table_name] = table_columns

    return table_info

