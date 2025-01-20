from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('me/', views.UserDetailView.as_view(), kwargs={'pk': 'me'}, name='user_me'),
]
