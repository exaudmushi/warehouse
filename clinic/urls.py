from django.urls import path
from.views import *

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('upload-and-verify/', MDBFileUploadAndVerifyView.as_view(), name='upload_and_verify'),
    path('successful/', DataUplodResponse.as_view(), name='successful'),

]
