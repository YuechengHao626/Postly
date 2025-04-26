from django.urls import path
from .views import UserRegistrationView, UserLoginView

urlpatterns = [
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', UserLoginView.as_view(), name='login'),
] 