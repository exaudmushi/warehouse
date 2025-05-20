from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
import requests

class MetricsData:
    permission_classes = [IsAuthenticated]

    def fetch_user_info(self, token, username):
   
        
        url = f"{settings.BASE_URL}/users/?query={username}"

        # Set headers with Bearer token
           # Set headers with Bearer token
        headers = {
            "Authorization": f"Bearer {token['access_token']}",
            "Content-Type": "application/json"
        }
        try:
            # Send GET request
            response = requests.get(url, headers=headers)
            
            # Check if request was successful
            if response.ok:
          
                return response.json()  # Return JSON response
            else:
                return f"Error {response.status_code}: {response.text}"  # Return error details
                
        except requests.RequestException as e:
            return f"Request failed: {str(e)}"
        
    def getTX_CURR(self, token, username):
        
        url = f"{settings.BASE_URL}/dataElements/?id={username}"

        # Set headers with Bearer token
           # Set headers with Bearer token
        headers = {
            "Authorization": f"Bearer {token['access_token']}",
            "Content-Type": "application/json"
        }
        try:
            # Send GET request
            response = requests.get(url, headers=headers)
            
            # Check if request was successful
            if response.ok:
          
                return response.json()  # Return JSON response
            else:
                return f"Error {response.status_code}: {response.text}"  # Return error details
                
        except requests.RequestException as e:
            return f"Request failed: {str(e)}"

        