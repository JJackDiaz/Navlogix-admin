from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('address/', views.planning, name='address'),
    path('save_step_data/<int:step>/', views.save_step_data, name='save_step_data'),
    path('upload_routes/<int:step>/', views.upload_routes, name='upload_routes'),
    path('complete_form/', views.complete_form, name='complete_form'),
    path('upload/', views.upload_file_view, name='upload_file'),
    path('createroutes/', views.create_routes, name='create_routes'),
]

