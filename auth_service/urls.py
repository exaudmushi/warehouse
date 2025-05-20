from django.urls import path
from .views import *


app_name = "auth_service"

urlpatterns = [
     path('', LoginAPIView.as_view(), name='home'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
     path('callback/', LoginAPIView.as_view(), name='callback'),
]