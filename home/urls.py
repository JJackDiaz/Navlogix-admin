from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('address/', views.address, name='address'),
    path('upload/', views.upload_file_view, name='upload_file'),
]

