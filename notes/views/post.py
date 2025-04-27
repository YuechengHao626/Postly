from django.shortcuts import get_object_or_404
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers import PostSerializer, CommentSerializer
from ..models import Post, SubForum, Comment

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
        # 从请求数据中获取子论坛ID
        subforum_id = self.request.data.get('subforum_id')
        if not subforum_id:
            raise serializers.ValidationError({"subforum_id": "This field is required."})
        
        # 获取子论坛对象
        subforum = get_object_or_404(SubForum, id=subforum_id)
        
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