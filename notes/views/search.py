from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from ..models import Post, SubForum
from ..serializers import PostSearchSerializer, SubForumSearchSerializer

class PostSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 搜索标题和内容
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'sub_forum').order_by('-created_at')
        
        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = posts.count()
        posts = posts[start:end]
        
        serializer = PostSearchSerializer(posts, many=True)
        
        return Response({
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        })

class SubForumSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 搜索名称和描述
        subforums = SubForum.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('created_by').annotate(
            post_count=Count('posts')
        ).order_by('-created_at')
        
        # 分页
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = subforums.count()
        subforums = subforums[start:end]
        
        serializer = SubForumSearchSerializer(subforums, many=True)
        
        return Response({
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'results': serializer.data
        }) 