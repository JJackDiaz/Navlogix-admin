from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #PLANNING
    path('planning/', views.planning, name='planning'),
    path('save_step_data/<int:step>/', views.save_step_data, name='save_step_data'),
    path('upload_routes/<int:step>/', views.upload_routes, name='upload_routes'),
    path('complete_form/', views.complete_form, name='complete_form'),
    path('createroutes/', views.create_routes, name='create_routes'),
    path('showroutes/', views.show_routes, name='show_routes'),
    path('get_session_data/', views.get_session_data, name='get_session_data'),
    path('delete_addresses/', views.delete_addresses_view, name='delete_addresses'),

    #MONITORING
    path('monitoring/', views.monitoring_index, name='monitoring_index'),

    #PLANNING MANAGEMENT
    path('planning-management/', views.planning_managemente_index, name='planning_managemente_index'),
    path('planning-management/<int:id>/detail', views.planning_managemente_details, name='planning_managemente_details'),

    #ROLES Y PERMISOS
    #FLOTAS
    path('fleets/', views.fleets_index, name='fleets_index'),
    path('fleets/<int:id>/', views.fleets_detail, name='fleets_detail'),
    #PREFERENCIAS
    #COMPANIES
    path('companies/', views.companies_index, name='companies_index'),
    path('companies/<int:id>/', views.company_detail, name='company_detail'),
    path('companies/<int:id>/delete/', views.company_delete, name='company_delete'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:company_id>/users/', views.company_users, name='company_users'),
    path('companies/<int:company_id>/users/create/', views.user_create, name='user_create'),

    #REFERENCES
    path('preferences/', views.preferences_index, name='preferences_index'),

    path('no-permission/', views.no_permission, name='no_permission'),
]








