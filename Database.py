import sqlite3
import pandas as pd
from fontTools.pens.basePen import NullPen


class Database:
    def __init__(self, db_path = "crypto_data"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self, table_name, columns, primary_keys=None):
        if primary_keys is None:
            primary_keys = []

        column_names = [column[0] for column in columns]
        for primary_key in primary_keys:
            if primary_key not in column_names:
                raise ValueError(f"{primary_key} not found in columns.")

        column_definitions = [f"{column[0]} {column[1]}" for column in columns]
        if primary_keys:
            column_definitions.append(f"PRIMARY KEY ({','.join(primary_keys)})")

        execution = f"CREATE TABLE IF NOT EXIST {table_name}({','.join(column_definitions)})"

        self.conn.execute(execution)
        self.conn.commit()

        print(f"Table {table_name} has been created.")
        return execution

    def create_index(self, table_name, index_table, column_name):
        self.conn.execute(f'''
        CREATE INDEX IF NOT EXISTS {index_table} 
        ON {table_name}({column_name})
        ''')

        self.conn.commit()

    def store_data(self, df, table_name):
        temp_table = df.copy()
        temp_table.to_sql("temp_table", self.conn, if_exists="replace", index=False)

        self.conn.execute(f'''
        INSERT OR IGNORE INTO {table_name}
        SELECT * FROM temp_table
        ''')

        self.conn.commit()

        self.conn.execute('''
        DROP TABLE temp_table
        ''')
        self.conn.commit()