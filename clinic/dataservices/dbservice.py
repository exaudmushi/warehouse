from pyspark.sql import SparkSession

class JsonToPostgresJob:
    def __init__(self, json_path, table_name, db_settings, unique_columns, jar_path):
        self.json_path = json_path
        self.table_name = table_name
        self.db_settings = db_settings
        self.unique_columns = unique_columns
        self.jar_path = jar_path

        self.jdbc_url = f"jdbc:postgresql://{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
        self.db_props = {
            "user": db_settings['USER'],
            "password": db_settings['PASSWORD'],
            "driver": "org.postgresql.Driver"
        }

        self.spark = SparkSession.builder \
            .appName("JsonToPostgres") \
            .config("spark.jars", jar_path) \
            .getOrCreate()

    def read_json(self):
        return self.spark.read.json(self.json_path)

    def read_existing_data(self, schema):
        try:
            return self.spark.read.jdbc(self.jdbc_url, self.table_name, properties=self.db_props)
        except Exception:
            # Table may not exist yet
            return self.spark.createDataFrame([], schema)

    def remove_duplicates(self, new_data, existing_data):
        return new_data.join(existing_data, on=self.unique_columns, how="left_anti")

    def write_data(self, data):
        data.write.jdbc(
            url=self.jdbc_url,
            table=self.table_name,
            mode='append',
            properties=self.db_props
        )

    def run(self):
        new_data = self.read_json()
        existing_data = self.read_existing_data(new_data.schema)
        filtered_data = self.remove_duplicates(new_data, existing_data)

        if filtered_data.count() > 0:
            self.write_data(filtered_data)
            print("✅ New records appended.")
        else:
            print("ℹ️ No new records to append.")

        self.spark.stop()
