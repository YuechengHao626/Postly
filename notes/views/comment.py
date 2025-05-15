from django.shortcuts import get_object_or_404
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from ..serializers import CommentSerializer
from ..models import Comment, Post, User, SubForumBan, ModeratorAssignment

class CommentViewSet(viewsets.ModelViewSet):
    """
    评论相关的视图集
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'delete']  # 允许删除方法

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # 检查用户是否被全局封禁
        if self.request.user.is_banned:
            raise PermissionDenied('You are banned from posting.')

        # 从请求数据中获取帖子ID和回复用户ID
        post_id = self.request.data.get('post_id')
        reply_to_user_id = self.request.data.get('reply_to_user_id')

        if not post_id:
            raise serializers.ValidationError({"post_id": "This field is required."})
        
        # 获取帖子对象
        post = get_object_or_404(Post, id=post_id)
        
        # 检查用户是否被子论坛封禁
        subforum_ban = SubForumBan.objects.filter(
            user=self.request.user,
            subforum=post.sub_forum,
            is_active=True
        ).first()
        
        if subforum_ban:
            raise PermissionDenied('You are banned from posting in this subforum.')
        
        # 验证回复用户ID
        reply_to_user = None
        if reply_to_user_id:
            try:
                reply_to_user = User.objects.get(id=reply_to_user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"reply_to_user_id": "Invalid user ID."}
                )
        
        # 创建评论
        serializer.save(
            author=self.request.user,
            post=post,
            reply_to_user=reply_to_user
        )

    def perform_destroy(self, instance):
        user = self.request.user

        # 超级管理员可以删除任何评论
        if user.role == 'super_admin':
            instance.delete()
            return

        # 检查用户是否是评论作者
        if instance.author == user:
            instance.delete()
            return

        # 检查用户是否是子论坛管理员或版主
        moderator = ModeratorAssignment.objects.filter(
            user=user,
            sub_forum=instance.post.sub_forum
        ).first()

        if moderator:
            instance.delete()
            return

        raise PermissionDenied('You do not have permission to delete this comment.') 