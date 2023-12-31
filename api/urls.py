from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.index, name='index'),
    path('files/<str:file_name>/', views.file_detail, name='file_detail'),
    path('files/delete/<str:file_name>/', views.delete_file, name='delete_file'),
]
