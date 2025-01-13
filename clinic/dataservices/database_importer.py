import psycopg2
import json
import datetime

class DatabaseImporter:
    def __init__(self, db_params, json_file_path):
    
        self.db_params = db_params
        self.json_file_path = json_file_path

    def create_table(self, cursor, table_name, data):
        """Create a table based on the JSON data's structure (all columns as TEXT)."""
        if len(data) == 0:
            return

        columns = data[0].keys()  # Get columns from the first row
        column_defs = [f"{column} TEXT" for column in columns]  # All columns as TEXT
        
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)});"
        cursor.execute(create_table_sql)


    def insert_data(self, cursor, table_name, data):
        """Insert data into the specified table."""
        if len(data) == 0:
            return
        
        columns = data[0].keys()
        placeholders = ', '.join(['%s' for _ in columns])  # PostgreSQL placeholder format
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
        
        for row in data:
            cursor.execute(insert_sql, tuple(row.values()))

    def import_json_to_db(self):
        """Import the data from the JSON file into the PostgreSQL database."""
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()

            # Load the JSON data
            with open(self.json_file_path, 'r') as json_file:
                json_data = json.load(json_file)

            # Process each table in the JSON file
            for table_name, data in json_data.items():
                # Create the table
                self.create_table(cursor, table_name, data)
                # Insert the data
                self.insert_data(cursor, table_name, data)

            # Commit the transaction
            conn.commit()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the database connection
            if conn:
                conn.close()

            print(f"Data imported into PostgreSQL database successfully!")
