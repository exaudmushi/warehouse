import os
import json
import pyodbc
import base64
from datetime import datetime
import concurrent.futures
import uuid
import random

class JsonConverter:
    def __init__(self, all_tables_data, output_folder,weekly_file):
        """
        Initializes the JsonConverter with table data and output filename.
        
        :param all_tables_data: Dictionary containing table names as keys and list of row dictionaries as values.
        :param output_filename: Name of the output JSON file.
        """
        self.all_tables_data = all_tables_data
        self.output_folder = output_folder
        self.weekly_file = weekly_file

    def datetime_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to string in ISO format
        raise TypeError(f"Type {type(obj)} not serializable")


    def convert_mdb_to_json(self, mdb_path):
        # Ensure the 'converted_json' folder exists at the root of the project
        converted_json_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'converted_json')
        if not os.path.exists(converted_json_dir):
            os.makedirs(converted_json_dir)
        
        # Get all .mdb files in the directory
        mdb_files = [f for f in os.listdir(mdb_path) if f.endswith('.mdb')]
        
        for mdb_file in mdb_files:
            mdb_file_path = os.path.join(mdb_path, mdb_file)
            
            # Connect to the .mdb file using pyodbc
            conn = pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_file_path};')
            cursor = conn.cursor()
            cursor2 = conn.cursor()
            
            # Iterate over all tables in the database and filter out system tables
            cursor.tables()
            cursor2.tables()
            tables = cursor.fetchall()
            tables2 = cursor.fetchall()
            
            # Filter out system tables that start with 'MSys'
            user_tables = [table for table in tables if not table.table_name.startswith('MSys')]
            
            all_tables_data = {}  # Dictionary to store data from all tables
            
            # Get the current date to append
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            uu_id = uuid.uuid4()

            
    
            for table in user_tables:
                table_name = table.table_name
                
                # Query the table and fetch data
                cursor.execute(f"SELECT * FROM {table_name}")
                columns = [column[0] for column in cursor.description]  # Extract column names
                rows = cursor.fetchall()
                

                 # Query the table and fetch data
                cursor2.execute(f"SELECT * FROM tblConfig")
                result = cursor2.fetchall()  # Fetch the first row
                # Store the result in the session variable
                hrfFacilityCode = result[0][3] if result else None
                # Convert rows to a list of dictionaries
              
                data = []
                for row in rows:
                    unique_row_id  = str(random.randint(111, 9999))
                    row_dict = {}
                    for i in range(len(columns)):
                        value = row[i]
                        if isinstance(value, bytes):  # Check if the value is binary data (bytes)
                            # Encode the bytes to base64 string
                            value = base64.b64encode(value).decode('utf-8')
                        row_dict[columns[i]] = value
                                 # Query the table and fetch data
    
                    # Add the current date to each row's data
                    row_dict["r_id"] = self.weekly_file +"-"+ hrfFacilityCode
                    row_dict["date_converted"] = current_date
                    row_dict["facility_name"] = hrfFacilityCode
                    row_dict["token"] =  str(uu_id)

                    data.append(row_dict)
                
                # Add the table data to the all_tables_data dictionary
                all_tables_data[table_name] = data
            
            # Create a single JSON file for the entire .mdb file with all tables
            json_filename = f"{mdb_file}.json"
            json_filepath = os.path.join(converted_json_dir, json_filename)
            
            with open(json_filepath, 'w') as json_file:
                json.dump(all_tables_data, json_file, indent=4, default=self.datetime_serializer)
           
            print(f"Converted all tables in {mdb_file} to a single JSON file at {json_filepath}")
            
            # Close the connection to the .mdb file
            conn.close()

