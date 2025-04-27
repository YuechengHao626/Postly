from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserLoginView, SubForumViewSet

router = DefaultRouter()
router.register(r'api/subforums', SubForumViewSet)

urlpatterns = [
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', UserLoginView.as_view(), name='login'),
    path('', include(router.urls)),
] 