from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers import SubForumSerializer, PostSerializer
from ..models import SubForum, ModeratorAssignment, Post, User
from ..permissions import IsNotBanned
import logging

logger = logging.getLogger(__name__)

class SubForumViewSet(viewsets.ModelViewSet):
    """
    子论坛相关的视图集
    """
    queryset = SubForum.objects.all()
    serializer_class = SubForumSerializer
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsNotBanned]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsNotBanned]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # 记录当前用户信息
        user = self.request.user
        logger.info(f"Creating subforum for user {user.username} (current role: {user.role})")

        # Set the creator of the subforum
        subforum = serializer.save(created_by=user)
        logger.info(f"Subforum created: {subforum.name}")
        
        # Create a ModeratorAssignment for the creator as subforum_admin
        ModeratorAssignment.objects.create(
            user=user,
            sub_forum=subforum,
            assigned_by=user,
            is_admin=True
        )
        logger.info(f"ModeratorAssignment created for user {user.username}")

        # Update user role to subforum_admin if not already a higher role
        if user.role not in ['super_admin', 'subforum_admin']:
            logger.info(f"Updating user role from {user.role} to subforum_admin")
            user.role = 'subforum_admin'
            user.save()
            
            # 验证角色是否已更新
            updated_user = User.objects.get(id=user.id)
            logger.info(f"User role after update: {updated_user.role}")
            
            # 强制刷新 request.user 对象
            if hasattr(self.request, '_cached_user'):
                delattr(self.request, '_cached_user')
            self.request.user = updated_user

    def create(self, request, *args, **kwargs):
        logger.info("Starting subforum creation process")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # 在返回响应前再次检查用户角色
        user = User.objects.get(id=request.user.id)
        logger.info(f"User role before sending response: {user.role}")
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """
        获取特定子论坛下的所有帖子
        """
        subforum = self.get_object()
        posts = Post.objects.filter(sub_forum=subforum).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data) 