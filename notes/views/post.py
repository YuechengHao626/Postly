from django.shortcuts import get_object_or_404
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from ..serializers import PostSerializer, CommentSerializer
from ..models import Post, SubForum, Comment, SubForumBan

class PostViewSet(viewsets.ModelViewSet):
    """
    帖子相关的视图集
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    http_method_names = ['get', 'post']  # 只允许 GET 和 POST 方法

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # 检查用户是否被全局封禁
        if self.request.user.is_banned:
            raise PermissionDenied('You are banned from posting.')
            
        # 从请求数据中获取子论坛ID
        subforum_id = self.request.data.get('subforum_id')
        if not subforum_id:
            raise serializers.ValidationError({"subforum_id": "This field is required."})
        
        # 获取子论坛对象
        subforum = get_object_or_404(SubForum, id=subforum_id)
        
        # 检查用户是否被子论坛封禁
        subforum_ban = SubForumBan.objects.filter(
            user=self.request.user,
            subforum=subforum,
            is_active=True
        ).first()
        
        if subforum_ban:
            raise PermissionDenied('You are banned from posting in this subforum.')
        
        # 创建帖子，设置作者和子论坛
        serializer.save(
            author=self.request.user,
            sub_forum=subforum
        )

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        获取特定帖子下的所有评论
        """
        post = self.get_object()
        comments = Comment.objects.filter(post=post).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data) 