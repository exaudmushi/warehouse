import os
import json
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
from ..models import FacilityEncryptedData
import datetime

class EncryptionService:
    def __init__(self, directory='uploaded_files'):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)


    def encrypt_data(self, data):
        """
        Encrypts the given data using the Fernet symmetric encryption method.
        """
        # Convert data to JSON format
        json_data = json.dumps(data, indent=4, default=self.datetime_serializer)

        # Generate a key for encryption (you should securely store this key)
        key = Fernet.generate_key()  # This should be stored securely
        cipher_suite = Fernet(key)

        # Encrypt the JSON data
        encrypted_data = cipher_suite.encrypt(json_data.encode())
        return encrypted_data, key

    def save_encrypted_file(self, encrypted_data,table_name):
        """
        Saves the encrypted data to a local file in the 'encrypted' folder.
        """
        encrypted_file_name = f"encrypted_{table_name}.json"
        encrypted_file_path = os.path.join(self.encrypted_directory, encrypted_file_name)

        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)

        return encrypted_file_path

    def upload_to_database(self, file_path, facility_code,facility_biom, encryption_key):
        """
        Uploads the encrypted file to the database using the FacilityEncryptedData model.
        """
        with open(file_path, 'rb') as encrypted_file:
            encrypted_file_content = encrypted_file.read()

            # Create a new FacilityEncryptedData object
            facility_encrypted_data = FacilityEncryptedData.objects.create(
                facility_name=facility_code,
                facility_biom = facility_biom,
                encrypted_file=ContentFile(encrypted_file_content, name=os.path.basename(file_path)),
                encryption_key=encryption_key  # Store the encryption key securely
            )

            print(f"Encrypted file uploaded to the database with ID: {facility_encrypted_data.id}")
            return facility_encrypted_data

    def delete_file(self, file_path):
        """
        Deletes the encrypted file from the local storage after uploading it to the database.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Encrypted file deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")

    def datetime_serializer(self, obj):
        """
        Custom serializer for datetime objects.
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

    def process_table_data(self, table_data, facility_code, facility_biom):
        """
        Processes the table data by encrypting it, saving it, and uploading it to the database.
        """
        encrypted_data, encryption_key = self.encrypt_data(table_data)

        # Save the encrypted data locally
        encrypted_file_path = self.save_encrypted_file(encrypted_data, facility_code)

        # Upload the encrypted file to the database
        facility_encrypted_data = self.upload_to_database(encrypted_file_path, facility_code,facility_biom, encryption_key)

        # Delete the local encrypted file after uploading it
        self.delete_file(encrypted_file_path)

        # Optionally, return the encryption key for future decryption (store it securely)
        return facility_encrypted_data
