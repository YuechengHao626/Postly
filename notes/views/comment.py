from django.shortcuts import get_object_or_404
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..serializers import CommentSerializer
from ..models import Comment, Post, User

class CommentViewSet(viewsets.ModelViewSet):
    """
    评论相关的视图集
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post']  # 只允许 GET 和 POST 方法

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # 从请求数据中获取帖子ID和回复用户ID
        post_id = self.request.data.get('post_id')
        reply_to_user_id = self.request.data.get('reply_to_user_id')

        if not post_id:
            raise serializers.ValidationError({"post_id": "This field is required."})
        
        # 获取帖子对象
        post = get_object_or_404(Post, id=post_id)
        
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