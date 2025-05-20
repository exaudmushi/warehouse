from django.db import models
from django.utils.timezone import now
from datetime import timedelta
from cryptography.fernet import Fernet
import json
import uuid


class DataFileUpload(models.Model):
    facility_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()  # in bytes
    time_upload = models.DateTimeField(default=now)
    expire_time = models.DateTimeField(default= now() + timedelta(days=30))
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.facility_name} - Uploaded on {self.time_upload}"

class Facility(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    ou = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.ou}"

    class Meta:
        verbose_name_plural = "Facilities"