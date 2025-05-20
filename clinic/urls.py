from django.urls import path
from .views import *
from .facility_views import *

app_name = "clinic"

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('about/', AboutView.as_view(), name='about'),
    path('app-admin/', AppAdminView.as_view(), name='app-admin'),
   
    path('admin/facilities/facility-list/', FacilityListView.as_view(), name='facility-list'),
    path('admin/facilities/facility-create/', FacilityCreateView.as_view(), name='facility-create'),
    path('admin/facilities/<uuid:id>/', FacilityDetailView.as_view(), name='facility-detail'),
    path('admin/facilities/<uuid:id>/edit/', FacilityUpdateView.as_view(), name='facility-update'),
    path('admin/facilities/<uuid:id>/delete/', FacilityDeleteView.as_view(), name='facility-delete'),




    path('upload/', DataPostingView.as_view(), name='data-posting'),
    path('process/', FileProcessingView.as_view(), name='file-processing'),
    path('import/', DataImportView.as_view(), name='data-import'),
    path('task/<str:task_id>/', TaskStatusView.as_view(), name='task-status')
]