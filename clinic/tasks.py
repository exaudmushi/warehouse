from celery import shared_task
import os
import zipfile
from django.conf import settings
from clinic.dataservices import servicefacility, file_converter
from clinic.dataservices.management.commands.data_importer import Command
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_file(file_path, file_name, user_id):
    output_messages = []
    try:
        # Extract ZIP
        extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted_files')
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        output_messages.append(("success", f"ZIP file extracted to {extract_path}"))
        logger.info(f"ZIP file {file_name} extracted by user {user_id}")

        # Convert MDB to JSON
        all_tables_data = {}
        format_name = servicefacility.HighlevelFunction
        data_file = format_name.format_filename(file_name)
        json_data_process = file_converter.JsonConverter(
            all_tables_data,
            output_folder=os.path.join(settings.BASE_DIR, 'clinic', 'dataservices', 'converted_json'),
            weekly_file=data_file
        )
        absolute_path = os.path.abspath(extract_path)
        clear_temp = servicefacility.HighlevelFunction
        clear_temp.clear_temp_files()
        json_data_process.convert_mdb_to_json(absolute_path)
        output_messages.append(("success", "MDB files converted to JSON"))
        logger.info(f"MDB files converted to JSON for {file_name}")

        # Run import_json command
        command = Command()
        command.handle(silent=True)
        output_messages.extend(command.get_output())
        logger.info(f"import_json command executed for {file_name}")
    except Exception as e:
        output_messages.append(("error", f"Error during processing: {str(e)}"))
        logger.error(f"Processing failed for {file_name}: {str(e)}")

    return [{"type": msg_type, "message": msg} for msg_type, msg in output_messages]