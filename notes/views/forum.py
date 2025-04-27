from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers import SubForumSerializer, PostSerializer
from ..models import SubForum, ModeratorAssignment, Post

class SubForumViewSet(viewsets.ModelViewSet):
    """
    子论坛相关的视图集
    """
    queryset = SubForum.objects.all()
    serializer_class = SubForumSerializer
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Set the creator of the subforum
        serializer.save(created_by=self.request.user)
        
        # Create a ModeratorAssignment for the creator as subforum_admin
        ModeratorAssignment.objects.create(
            user=self.request.user,
            sub_forum=serializer.instance,
            assigned_by=self.request.user,
            is_admin=True
        )

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """
        获取特定子论坛下的所有帖子
        """
        subforum = self.get_object()
        posts = Post.objects.filter(sub_forum=subforum).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data) 