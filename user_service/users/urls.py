from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile endpoints
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # User search and details endpoints
    path('search/', views.UserSearchView.as_view(), name='user-search'),
    path('by-id/<int:pk>/', views.UserDetailByIdView.as_view(), name='user-detail-by-id'),
    
    # User list and delete endpoints
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/delete/<int:user_id>/', views.DeleteUserView.as_view(), name='user-delete'),
path('validate_token/', views.ValidateTokenView.as_view(), name='token-validate'),
]
# Token validation endpoint
