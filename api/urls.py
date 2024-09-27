from django.urls import path
from .views import (CompanyListCreateView, CompanyRetrieveUpdateDestroyView,
                    FleetListCreateView, FleetRetrieveUpdateDestroyView,
                    AddressListCreateView, AddressRetrieveUpdateDestroyView,
                    VehicleListCreateView, VehicleRetrieveUpdateDestroyView,
                    RouteListCreateView, RouteRetrieveUpdateDestroyView,
                    RouteAddressListCreateView, RouteAddressRetrieveUpdateDestroyView,
                    VehicleActiveRouteView, UserRoutesView, LoginView, Logout, UserRoutesView, DetailRoutesView)

urlpatterns = [
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', Logout.as_view(), name = 'api_logout'),

    # Compañías
    path('companies/', CompanyListCreateView.as_view(), name='company-list'),
    path('companies/<int:pk>/', CompanyRetrieveUpdateDestroyView.as_view(), name='company-detail'),

    # Flotas
    path('fleets/', FleetListCreateView.as_view(), name='fleet-list'),
    path('fleets/<int:pk>/', FleetRetrieveUpdateDestroyView.as_view(), name='fleet-detail'),

    # Direcciones
    path('addresses/', AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressRetrieveUpdateDestroyView.as_view(), name='address-detail'),

    # Vehículos
    path('vehicles/', VehicleListCreateView.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', VehicleRetrieveUpdateDestroyView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:vehicle_id>/active-route/', VehicleActiveRouteView.as_view(), name='vehicle-active-route'),

    # Rutas
    path('user-routes/<int:user_id>/', UserRoutesView.as_view(), name='user-routes'),
    path('detail-routes/<int:pk>/', DetailRoutesView.as_view(), name='detail-routes'),

    path('routes/', RouteListCreateView.as_view(), name='route-list'),
    path('routes/<int:pk>/', RouteRetrieveUpdateDestroyView.as_view(), name='route-detail'),

    # Direcciones de la Ruta
    path('route-addresses/', RouteAddressListCreateView.as_view(), name='route-address-list'),
    path('route-addresses/<int:pk>/', RouteAddressRetrieveUpdateDestroyView.as_view(), name='route-address-detail'),

    # Rutas de usuario
    path('user-routes/', UserRoutesView.as_view(), name='user-routes'),
]
