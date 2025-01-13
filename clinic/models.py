from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from cryptography.fernet import Fernet
import json

class HRFCodeFacility(models.Model):
    hrf_code = models.CharField(max_length=20, unique=True)
    facility_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.facility_name} ({self.hrf_code})"


class DataFileUpload(models.Model):
    facility_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()  # in bytes
    time_upload = models.DateTimeField(default=now)
    expire_time = models.DateTimeField(default= now() + timedelta(days=30))
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.facility_name} - Uploaded on {self.time_upload}"


class FacilityEncryptedData(models.Model):
    facility_name = models.CharField(max_length=255)
    facility_biom = models.CharField(max_length=255, default="")
    encrypted_file = models.FileField(upload_to='encrypted_data/')
    encryption_key = models.CharField(max_length=255, blank=True, null=True)  # You can store the encryption key securely
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Encrypted Data for {self.table_name} - {self.created_at}"