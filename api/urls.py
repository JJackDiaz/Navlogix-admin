from django.urls import path
from .views import LoginView, Logout, UserRoutesView

urlpatterns = [
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', Logout.as_view(), name = 'api_logout'),
    path('user-routes/<int:user_id>/', UserRoutesView.as_view(), name='user-routes'),
]
