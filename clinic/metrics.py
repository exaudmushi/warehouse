from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
        
    def getTX_CURR(self, token):
        
        TX_CURR = "analytics.json?dimension=dx:CW9ROzDWRiq&dimension=pe:202410&dimension=ou:wI14U2j7n7q&aggregationType=SUM"
        url = f"{settings.BASE_URL}/{TX_CURR}"

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
        
    def getTX_PMTCT_STAT(self, token):
        
        PMTCT_ANC1 = "analytics.json?dimension=dx:rCeCpvmTzK4&dimension=pe:202410&dimension=ou:wI14U2j7n7q&aggregationType=SUM"
        url = f"{settings.BASE_URL}/{PMTCT_ANC1}"

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
        
    def getTX_PMTCT_HEI(self, token):
        
        PMTCT_HEI = "analytics?dimension=dx:A9o8ET4K9wH&dimension=co&dimension=pe:202410&dimension=ou:wI14U2j7n7q&displayProperty=NAME&includeMetadataDetails=true"
        url = f"{settings.BASE_URL}/{PMTCT_HEI}"

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
        
    def getTX_PMTCT_EID(self, token):
        
        PMTCT_EID = "analytics?dimension=dx:Jm6ETCXn8kA&dimension=co&dimension=pe:202410&dimension=ou:wI14U2j7n7q&displayProperty=NAME&includeMetadataDetails=true"
        url = f"{settings.BASE_URL}/{PMTCT_EID}"

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

        