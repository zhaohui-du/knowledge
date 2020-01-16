from django.urls import path
from . import views


app_name = 'study'

urlpatterns = [
    path('', views.index, name='index'),
    path('to_login/', views.to_login, name='to_login'),
    path('user_login/', views.user_login, name='user_login'),
    path('system_view/', views.system_view, name='system_view'),
    path('system_pdf_view/<str:system_name>/', views.system_pdf_view, name='system_pdf_view'),
    path('system_admin/', views.system_admin, name='system_admin'),
    path('system_pdf_admin/<str:system_name>/', views.system_pdf_admin, name='system_pdf_admin'),
    path('to_operation/<str:name>/<str:operation>/', views.to_operation, name='to_operation'),
    path('pdf_file_upload/', views.pdf_file_upload, name='pdf_file_upload'),
    path('pdf_file_delete/', views.pdf_file_delete, name='pdf_file_delete'),
    path('to_pdf_delete/<str:system_name>/', views.to_pdf_delete, name='to_pdf_delete'),
    path('to_system_delete/', views.to_system_delete, name='to_system_delete'),
    path('pdf_files_delete/', views.pdf_files_delete, name='pdf_files_delete'),
    path('systems_delete/', views.systems_delete, name='systems_delete'),
    path('system_add/', views.system_add, name='system_add'),
    path('system_delete/', views.system_delete, name='system_delete'),
    path('pdf_file_search/', views.pdf_file_search, name='pdf_file_search'),

]
