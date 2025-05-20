# your_app/management/commands/import_json.py
import os
import json
import django
from django.core.management.base import BaseCommand
from django.conf import settings
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


class Command(BaseCommand):
    help = "Import multiple JSON files into PostgreSQL, each to its own table"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_messages = []

    def add_arguments(self, parser):
        parser.add_argument("--silent", action="store_true", help="Suppress console output")

    def handle(self, *args, **kwargs):
        silent = kwargs.get("silent", False)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multi_clinic.settings")
        django.setup()

        db = settings.DATABASES["default"]
        json_dir = os.path.join(settings.BASE_DIR, "clinic/dataservices/converted_json")

        if not os.path.exists(json_dir):
            msg = f"JSON directory does not exist: {json_dir}"
            self.output_messages.append(("error", msg))
            if not silent:
                self.stderr.write(msg)
            return

        spark = SparkSession.builder \
            .appName("ImportJSON") \
            .config("spark.jars", os.path.join(settings.BASE_DIR, "clinic/dataservices/postgresql-connector.jar")) \
            .getOrCreate()

        jdbc_url = f"jdbc:postgresql://{db['HOST']}:{db['PORT']}/{db['NAME']}"
        jdbc_props = {
            "user": db["USER"],
            "password": db["PASSWORD"],
            "driver": "org.postgresql.Driver"
        }

        try:
            for file in os.listdir(json_dir):
                if not file.endswith(".json"):
                    continue
                file_path = os.path.join(json_dir, file)
                with open(file_path, "r") as f:
                    json_data = json.load(f)
                if not isinstance(json_data, dict):
                    msg = f"Skipping invalid JSON format in {file}"
                    self.output_messages.append(("error", msg))
                    if not silent:
                        self.stderr.write(msg)
                    continue
                for table_name, records in json_data.items():
                    if not records:
                        msg = f"Skipping empty table '{table_name}' in {file}"
                        self.output_messages.append(("info", msg))
                        if not silent:
                            self.stdout.write(msg)
                        continue
                    temp_file = os.path.join(json_dir, f"temp_{table_name}.json")
                    with open(temp_file, "w") as tmp:
                        json.dump(records, tmp)
                    df = spark.read.json(temp_file)
                    bigint_fields = ["EACStageID", "ResultsStatusID", "NumDaysDispensed", "ARVCode", "ARVStatusCode", "WHOStage", "UserNumber"]
                    for field in bigint_fields:
                        if field in df.columns:
                            df = df.withColumn(field, col(field).cast("long"))

                    if table_name == "tblCT":
                        cast_fields_ct = ["TCOfferingStatus", "NoOfContactsElicited", "MissingFPReasonID",
                                        "UserNumberLastEdit", "xUserNumber", "xUserNumberCounsellor","CondomsIssuedFemale"]
                        for field in cast_fields_ct:
                            if field in df.columns:
                                df = df.withColumn(field, col(field).cast("long"))

                    elif table_name == "tblTests":
                        cast_fields_tests = ["ResultsStatusID", "IsTransferIn", "OutcomeUpdatedThroughIntegration",
                                            "PartialUpdateThroughIntegration", "TestTypeID", "TheID", "TransferInRecGUID"]
                        for field in cast_fields_tests:
                            if field in df.columns:
                                df = df.withColumn(field, col(field).cast("long"))
                        
                    elif table_name == "tblFamilyInfo":
                        cast_fields_tests = ["RelativeID"]

                        for field in cast_fields_tests:
                            if field in df.columns:
                                df = df.withColumn(field, col(field).cast("long"))

                    elif table_name == "tblReturningClients":
                        cast_fields_tests = ["TotalRequiredDosageNumberOfDaysIPT"]

                        for field in cast_fields_tests:
                            if field in df.columns:
                                df = df.withColumn(field, col(field).cast("long"))

                    df.write.jdbc(url=jdbc_url, table=table_name, mode="append", properties=jdbc_props)
                    os.remove(temp_file)
                    msg = f"Imported {len(records)} records into '{table_name}' from {file}"
                    self.output_messages.append(("success", msg))
                    if not silent:
                        self.stdout.write(self.style.SUCCESS(msg))
        except Exception as e:
            msg = f"Import failed: {str(e)}"
            self.output_messages.append(("error", msg))
            if not silent:
                self.stderr.write(msg)
        finally:
            spark.stop()

    def get_output(self):
        return self.output_messages