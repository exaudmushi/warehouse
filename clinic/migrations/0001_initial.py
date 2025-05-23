# Generated by Django 5.1.4 on 2025-05-20 17:34

import datetime
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataFileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facility_name', models.CharField(max_length=255)),
                ('size', models.PositiveIntegerField()),
                ('time_upload', models.DateTimeField(default=django.utils.timezone.now)),
                ('expire_time', models.DateTimeField(default=datetime.datetime(2025, 6, 19, 17, 34, 44, 528656, tzinfo=datetime.timezone.utc))),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('ou', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Facilities',
            },
        ),
        migrations.CreateModel(
            name='HRFCodeFacility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hrf_code', models.CharField(max_length=20, unique=True)),
                ('facility_name', models.CharField(max_length=255)),
            ],
        ),
    ]
