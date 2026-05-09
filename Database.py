import sqlite3
from logging import exception
import pandas as pd

class Database:
    def __init__(self, db_path = "crypto_data"):
        self.conn = sqlite3.connect(db_path)

    def create_table(self, table_name, columns, primary_keys=None):
        if primary_keys is None:
            primary_keys = []

        column_names = [column[0] for column in columns]
        for primary_key in primary_keys:
            if primary_key not in column_names:
                raise ValueError(f"{primary_key} not found in columns.")

        column_definitions = [f"{column_name} {column_type}" for column_name, column_type in columns]
        if primary_keys:
            column_definitions.append(f"PRIMARY KEY ({','.join(primary_keys)})")

        execution = f"CREATE TABLE IF NOT EXISTS {table_name}({','.join(column_definitions)})"

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

    def get_table_names(self):
        table_names = self.conn.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name NOT like 'sqlite_'
        ''').fetchall()

        return table_names

    def delete_table(self, table_name):
        try:
            self.conn.execute(f'''
            DROP TABLE IF EXISTS {table_name}
            ''')
            self.conn.commit()
            print(f"Table {table_name} deleted")
            return True
        except exception as e:
            print(e)
            return False

    def if_table_exist(self, table_name):
        try:
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            return count >= 1
        except Exception as e:
            return e

    def verify_storage(self, symbol):
        count = self.conn.execute(f"SELECT COUNT(*) FROM price_data WHERE symbol = {symbol}").fetchone()[0]

        latest = self.conn.execute(f"SELECT MAX(open_time) FROM price_data WHERE symbol = {symbol}").fetchone()[0]

        print(f"✅ {symbol}: {count} rows, latest: {latest}")

        return count, latest