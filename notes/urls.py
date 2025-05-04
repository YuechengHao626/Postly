from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views.auth import UserRegistrationView, UserLoginView
from .views.forum import SubForumViewSet
from .views.post import PostViewSet
from .views.comment import CommentViewSet
from .views.vote import VoteCreateAPIView
from .views.ban import global_ban_user, subforum_ban_user, subforum_unban_user
from .views.search import PostSearchView, SubForumSearchView

router = DefaultRouter()
router.register(r'api/subforums', SubForumViewSet)
router.register(r'api/posts', PostViewSet)
router.register(r'api/comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', UserLoginView.as_view(), name='login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/votes/', VoteCreateAPIView.as_view(), name='vote-create'),
    path('api/admin/ban/', global_ban_user, name='global-ban-user'),
    path('api/moderator/ban/', subforum_ban_user, name='subforum-ban-user'),
    path('api/moderator/unban/', subforum_unban_user, name='subforum-unban-user'),
    path('api/search/posts/', PostSearchView.as_view(), name='post-search'),
    path('api/search/subforums/', SubForumSearchView.as_view(), name='subforum-search'),
] 