from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, 
    UserProfileView, 
    UserUpdateView,
    CustomTokenObtainPairView
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
]

