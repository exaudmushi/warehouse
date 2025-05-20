import os 
import pyodbc
import shutil
import tempfile

class HighlevelFunction:

    def HRFCode(mdb_path):
        
        # Get all .mdb files in the directory
        mdb_files = [f for f in os.listdir(mdb_path) if f.endswith('.mdb')]
        
        for mdb_file in mdb_files:
            mdb_file_path = os.path.join(mdb_path, mdb_file)
            
            # Connect to the .mdb file using pyodbc
            conn = pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={mdb_file_path};')
            cursor = conn.cursor()
            
            # Iterate over all tables in the database and filter out system tables
            cursor.tables()

            # Query the table and fetch data
            cursor.execute(f"SELECT * FROM tblConfig")
           # rows = cursor.fetchall()
            result = cursor.fetchall()  # Fetch the first row

            # Store the result in the session variable
            hrfFacilityCode = result[0][3] if result else None
            print(hrfFacilityCode)
            # Close the connection to the .mdb file
            conn.close()
        return hrfFacilityCode

    def clear_temp_files():
        # Get the system's default temporary directory
        temp_dir = tempfile.gettempdir()

        # List all files and folders in the temp directory
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            # Delete all files in the temp directory
            for name in files:
                try:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)  # Delete file
                    
                except Exception as e:
                    pass # print(f"Failed to delete {file_path}: {e}")
            
            # Delete all empty directories in the temp folder
            for name in dirs:
                try:
                    dir_path = os.path.join(root, name)
                    os.rmdir(dir_path)  # Delete directory (only if empty)
                
                except Exception as e:
                    pass #print(f"Failed to delete {dir_path}: {e}")


    def format_filename(file_path):
        # Split the filename and extension
        file_name, file_extension = os.path.splitext(file_path)
        
        # Return the filename without the extension
        return file_name
    
    