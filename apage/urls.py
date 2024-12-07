from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.base, name='index'),  # Home page
    path('home/', views.home, name='home'),  # Match to this URL
    path('sucess/',views.success,name='success'),
    # service report 
    # path('service-report/<int:pk>/', views.servicereport, name='servicereport_detail'),
    path('servicereport/', views.servicereport, name='servicereport'),  # Match to this URL
    path('service-reports/', views.service_report_list, name='service_report_list'),
    path('service-report/<int:pk>/', views.view_service_report, name='view_service_report'),
    path('export/service_report/<str:format>/', views.export_service_report, name='export_service_report'),

    # general report 
    path('generalreport/', views.generalreport, name='generalreport'),  # Match to this URL
    path('generate_pdf/<int:report_id>/', views.generate_pdf, name='generate_pdf'),
    path('view-reports/', views.generalreportsviewing, name='generalreportsviewing'),
    # MOM
    path('mom/', views.mom, name='mom'),  # Match to this URL
    path('mom/records/', views.mom_records, name='mom_records'),  # New view to display records
    path('mom/detail/<int:mom_id>/', views.mom_detail, name='mom_detail'),  # View individual MOM details
    # Maintenance Checklist 
    path('maintenance-checklist/', views.maintenance_checklist, name='maintenance_checklist'),
    path('maintenance-records/', views.maintenance_checklist_records, name='maintenance_checklist_records'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)