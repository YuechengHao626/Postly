from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, 
    UserLoginView, 
    SubForumViewSet, 
    PostViewSet,
    CommentViewSet,
    VoteCreateAPIView
)

router = DefaultRouter()
router.register(r'api/subforums', SubForumViewSet)
router.register(r'api/posts', PostViewSet)
router.register(r'api/comments', CommentViewSet)

urlpatterns = [
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', UserLoginView.as_view(), name='login'),
    path('api/votes/', VoteCreateAPIView.as_view(), name='vote-create'),
    path('', include(router.urls)),
] 