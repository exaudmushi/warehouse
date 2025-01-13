import os
import json
from datetime import datetime
from .database_importer import DatabaseImporter


class JSONDataWriter:
    def __init__(self, all_tables_data, directory='facility_json_data'):
        self.all_tables_data = all_tables_data  # This is expected to be a dictionary of table names and their data
        self.directory = directory
        # Ensure the directory exists
        os.makedirs(self.directory, exist_ok=True)

    # Custom datetime serializer
    def datetime_serializer(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to string in ISO format
        raise TypeError(f"Type {type(obj)} not serializable")

    # Method to add HRFCode to each row of the data
    def add_hrf_code_to_data(self, data, hrf_code):
        """ Adds the HRFCode to each row in the data. """
        for row in data:
            row['HRFCode'] = hrf_code
        return data

    # Method to process (serialize) each table's data
    def process_table_data(self, table_name, hrf_code, data):
        # Add HRFCode to each row of data
        data_with_hrf_code = self.add_hrf_code_to_data(data, hrf_code)
        
        # Convert the data to JSON with pretty print and custom datetime serializer
        return {table_name: json.dumps(data_with_hrf_code, indent=4, default=self.datetime_serializer)}

    def write_all_tables(self, hrf_code, facility_name,setupDB):
        # Generate the output path
        output_path = os.path.join(self.directory, f"{facility_name}.json")
        
        try:
            # Check if the file already exists
            if os.path.exists(output_path):
                print(f"File {output_path} already exists.")
                # Optionally handle overwriting or skipping
                overwrite = input("Do you want to overwrite it? (yes/no): ").strip().lower()
                if overwrite != 'yes':
                    print("Skipping the file write operation.")
                    return

            all_data = {}
            for table_name, data in self.all_tables_data.items():
                # Process data to include HRFCode and then convert to JSON
                all_data[table_name] = json.loads(self.process_table_data(table_name, hrf_code, data)[table_name])
            
            # Import data into the database
            importer = DatabaseImporter(setupDB, output_path)
            importer.import_json_to_db()
            
            # Write data to JSON
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4,default=self.datetime_serializer)



            print(f"Data successfully written to {output_path}")

        except Exception as e:
            print(f"An error occurred: {e}")
    

