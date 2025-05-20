from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import requests_mock
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings
from django.test import RequestFactory
from .views import DataPostingView

class DataServiceTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = RequestFactory()
        self.token = 'valid-jwt-token'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.file_content = b'dummy zip content'
        self.uploaded_file = SimpleUploadedFile('test.zip', self.file_content, content_type='application/zip')

    def test_data_posting_view_get(self):
        request = self.factory.get('/upload/')
        response = DataPostingView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('upload.html', response.template_name)

    def test_data_posting_view_post_success(self):
        with requests_mock.Mocker() as m:
            m.post(
                'http://auth-service:8000/api/validate-token/',
                json={'valid': True, 'payload': {'username': 'testuser', 'user_id': '123', 'roles': [{'name': 'data_entry'}]}},
                status_code=200
            )
            response = self.client.post(
                '/upload/',
                {'file': self.uploaded_file, 'token': self.token},
                format='multipart'
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn('successful.html', response.template_name)
            self.assertIn('task_id', response.data)
            file_path = response.data['file_path']
            self.assertTrue(os.path.exists(file_path))
            os.remove(file_path)

    def test_data_posting_view_invalid_token(self):
        with requests_mock.Mocker() as m:
            m.post(
                'http://auth-service:8000/api/validate-token/',
                json={'error': 'Invalid token'},
                status_code=401
            )
            response = self.client.post(
                '/upload/',
                {'file': self.uploaded_file, 'token': 'invalid-token'},
                format='multipart'
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn('upload.html', response.template_name)
            self.assertIn('errors', response.data['form'])

    def test_task_status_view(self):
        with requests_mock.Mocker() as m:
            m.post(
                'http://auth-service:8000/api/validate-token/',
                json={'valid': True, 'payload': {'username': 'testuser', 'user_id': '123', 'roles': [{'name': 'data_entry'}]}},
                status_code=200
            )
            # Simulate a completed task (requires Celery setup)
            response = self.client.get('/task/dummy-task-id/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('status', response.data)