import pyodbc
from django.db import models

class AccessDatabaseManager(models.Manager):
    def __init__(self, mdb_file_path):
        self.mdb_file_path = mdb_file_path
        self.connection = self.connect_to_mdb()
        super().__init__()

    def connect_to_mdb(self):
        connection_string = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + self.mdb_file_path + ';'
        )
        connection = pyodbc.connect(connection_string)
        return connection

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def close_connection(self):
        if self.connection:
            self.connection.close()

# Example usage in a Django model
class AccessData(models.Model):
    custom_field = models.CharField(max_length=255)

    objects = AccessDatabaseManager(mdb_file_path=r'C:\path\to\your\file.mdb')

# Example of how to query data
# Use this code where needed, e.g., in views, or other parts of your Django app
def fetch_access_data():
    query = 'SELECT * FROM YourTableName'
    results = AccessData.objects.execute_query(query)
    for result in results:
        print(result)


