from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import logging
from .serializers import LoginSerializer
import base64

logger = logging.getLogger(__name__)

class LoginAPIView(APIView):
    template_name = 'login.html'

    def get(self, request):
        token = request.session.get('dhis2_token')
        context = {
            'is_authenticated': bool(token and 'access_token' in token),
            'message': 'User is authenticated' if token and 'access_token' in token else 'User is not authenticated',
        }
        from django.shortcuts import render
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
           
            # Encode client credentials in Base64
            credentials = f"{settings.CLIENT_ID}:{settings.CLIENT_SECRET}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
             # Set headers
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            # Set payload
            payload = {
                "grant_type": "password",
                "username": username,
                "password": password
            }

            # Send request
            response = requests.post(settings.TOKEN_URL, headers=headers, data=payload)

            if response.status_code == 200:
                try:
                    token = response.json()
                    request.session['app_token'] = token
                    request.session['username'] = username
                    return Response({'message': 'Login successful','base_url':settings.BASE_URL}, status=200)
                except ValueError as e:
                    logger.error(f"JSON parse error: {e}, content: {response.text[:1000]}")
                    return Response({'error': 'Invalid DHIS2 response'}, status=500)
            else:
                logger.error(f"DHIS2 error: {response.status_code} - {response.text[:1000]}")
                error_msg = 'Redirected to login' if response.status_code == 302 else 'Authentication failed'
                return Response({'error': error_msg}, status=401)

        except requests.exceptions.RequestException as e:
            logger.error(f"DHIS2 connection failed: {e}")
            return Response({'error': 'DHIS2 unreachable'}, status=503)

class LogoutView(RedirectView):
    url = reverse_lazy('home')  # Set to a valid URL, e.g., reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        request.session.flush()
        return super().get(request, *args, **kwargs)