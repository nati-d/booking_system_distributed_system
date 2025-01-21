from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User management endpoints
    path('me/', views.UserDetailView.as_view(), kwargs={'pk': 'me'}, name='user-me'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
