from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.generic import TemplateView
from django.shortcuts import render
import requests
import os
import json
import zipfile
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from decouple import config
from .serializers import FileUploadSerializer, FileProcessingSerializer
from .tasks import process_file
from celery.result import AsyncResult
from clinic.dataservices import servicefacility, file_converter
from clinic.dataservices.management.commands.data_importer import Command
import base64
from clinic.metrics import MetricsData
from .serializers import GetParameters

logger = logging.getLogger(__name__)

class AppAdminView(TemplateView, APIView):
    template_name = 'admin/home.html'
    
    def get(self, request, *args, **kwargs):
    
        token = request.session['app_token']
       
        username = request.session['username']

        try:
           response = MetricsData.fetch_user_info(self, token, username)
           context = {
               'results':response
           }
        

        except requests.exceptions.RequestException as e:
            logger.error(f"DHIS2 connection failed: {e}")
            return Response({'error': 'DHIS2 unreachable'}, status=503)
    
        return render(request, self.template_name,context=context)
    

class DashboardView(TemplateView, APIView):
    """
    Renders upload form (GET) and handles file upload (POST).
    """
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
    
        token = request.session['app_token']
       
        username = request.session['username']

        try:
           response = MetricsData.fetch_user_info(self, token, username)
           context = {
               'results':response
           }
        

        except requests.exceptions.RequestException as e:
            logger.error(f"DHIS2 connection failed: {e}")
            return Response({'error': 'DHIS2 unreachable'}, status=503)
    
        return render(request, self.template_name,context=context)

class ProfileView(TemplateView, APIView):
    template_name = 'profile/profile.html'

    def get(self, request, *args, **kwargs):
     
        token = request.session['app_token']

        username = request.session['username']

        try:
           response = MetricsData.fetch_user_info(self, token, username)
           context = {
               'results':response
           }
        except requests.exceptions.RequestException as e:
                logger.error(f"DHIS2 connection failed: {e}")
                return Response({'error': 'DHIS2 unreachable'}, status=503)

        return render(request, self.template_name,context=context)
    
class AboutView(TemplateView, APIView):
    template_name = 'profile/about.html'

    def get(self, request, *args, **kwargs):
     
        return render(request, self.template_name)

class DataPostingView(TemplateView, APIView):
    """
    Renders upload form (GET) and handles file upload (POST).
    """
    template_name = 'upload.html'

    def get(self, request, *args, **kwargs):
        # Render upload form
        token = request.GET.get('token', '')  # Optional: Pass JWT via query param or session
        
        return render(request, self.template_name, {'token': token})

    def post(self, request, *args, **kwargs):
        # Validate request
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return render(request, self.template_name, {
                'form': {'errors': serializer.errors},
                'token': request.data.get('token', '')
            })

        # Extract and validate JWT
        token = request.data.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return render(request, self.template_name, {
                'form': {'errors': {'token': ['Authorization token required']}},
                'token': ''
            })

        auth_url = f"{config('AUTH_SERVICE_URL')}/api/validate-token/"
        try:
            auth_response = requests.post(auth_url, json={'token': token})
            if auth_response.status_code != 200:
                return render(request, self.template_name, {
                    'form': {'errors': {'token': [auth_response.json().get('error', 'Invalid token')]}},
                    'token': token
                })
            auth_data = auth_response.json()
            logger.info(f"Token validated for user: {auth_data['payload']['username']}")
        except requests.RequestException as e:
            logger.error(f"Failed to validate token: {str(e)}")
            return render(request, self.template_name, {
                'form': {'errors': {'token': [f'Failed to validate token: {str(e)}']}},
                'token': token
            })

        # Save uploaded file
        uploaded_file = serializer.validated_data['file']
        directory = os.path.join('uploaded_files')
        os.makedirs(os.path.join(settings.MEDIA_ROOT, directory), exist_ok=True)

        uploaded_file_name = uploaded_file.name
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        filename = fs.save(os.path.join(directory, uploaded_file_name), uploaded_file)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        logger.info(f"File {uploaded_file_name} saved to {file_path}")

        # Start asynchronous processing
        task = process_file.delay(file_path, uploaded_file_name, auth_data['payload']['user_id'])
        output_messages = [("info", "File upload accepted, processing started")]

        # Render success template
        messages_json = [{"type": msg_type, "message": msg} for msg_type, msg in output_messages]
        return render(request, 'successful.html', {
            'messages': messages_json,
            'task_id': task.id,
            'file_path': file_path
        })

class FileProcessingView(APIView):
    """
    Synchronous endpoint for ZIP extraction and MDB-to-JSON conversion.
    """
    def post(self, request):
        serializer = FileProcessingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return Response(
                {'error': 'Authorization token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        auth_url = f"{config('AUTH_SERVICE_URL')}/api/validate-token/"
        try:
            auth_response = requests.post(auth_url, json={'token': token})
            if auth_response.status_code != 200:
                return Response(auth_response.json(), status=status.HTTP_401_UNAUTHORIZED)
            auth_data = auth_response.json()
            logger.info(f"Token validated for user: {auth_data['payload']['username']}")
        except requests.RequestException as e:
            logger.error(f"Failed to validate token: {str(e)}")
            return Response(
                {'error': f'Failed to validate token: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        file_path = serializer.validated_data['file_path']
        file_name = os.path.basename(file_path)
        output_messages = []

        try:
            extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted_files')
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            output_messages.append(("success", f"ZIP file extracted to {extract_path}"))

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
        except Exception as e:
            output_messages.append(("error", f"Error during processing: {str(e)}"))
            logger.error(f"Processing failed for {file_name}: {str(e)}")

        messages_json = [{"type": msg_type, "message": msg} for msg_type, msg in output_messages]
        return Response(
            {'messages': messages_json},
            status=status.HTTP_200_OK if not any(msg['type'] == 'error' for msg in messages_json) else status.HTTP_400_BAD_REQUEST
        )

class DataImportView(APIView):
    """
    Synchronous endpoint for running import_json command.
    """
    def post(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return Response(
                {'error': 'Authorization token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        auth_url = f"{config('AUTH_SERVICE_URL')}/api/validate-token/"
        try:
            auth_response = requests.post(auth_url, json={'token': token})
            if auth_response.status_code != 200:
                return Response(auth_response.json(), status=status.HTTP_401_UNAUTHORIZED)
            auth_data = auth_response.json()
            logger.info(f"Token validated for user: {auth_data['payload']['username']}")
        except requests.RequestException as e:
            logger.error(f"Failed to validate token: {str(e)}")
            return Response(
                {'error': f'Failed to validate token: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        output_messages = []
        try:
            command = Command()
            command.handle(silent=True)
            output_messages.extend(command.get_output())
            logger.info("import_json command executed")
        except Exception as e:
            output_messages.append(("error", f"Error during import: {str(e)}"))
            logger.error(f"Import failed: {str(e)}")

        messages_json = [{"type": msg_type, "message": msg} for msg_type, msg in output_messages]
        return Response(
            {'messages': messages_json},
            status=status.HTTP_200_OK if not any(msg['type'] == 'error' for msg in messages_json) else status.HTTP_400_BAD_REQUEST
        )

class TaskStatusView(APIView):
    """
    Checks the status of an asynchronous processing task.
    """
    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {'status': 'pending'}
        elif task.state == 'SUCCESS':
            response = {'status': 'success', 'result': task.result}
            # Render template for web access
            if request.GET.get('format') != 'json':
                return render(request, 'successful.html', {
                    'messages': task.result,
                    'task_id': task_id,
                    'file_path': ''  # Optional: Retrieve from database
                })
        elif task.state == 'FAILURE':
            response = {'status': 'failed', 'error': str(task.result)}
        else:
            response = {'status': task.state}
        return Response(response)