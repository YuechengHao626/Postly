from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from ..models import User
from ..serializers import UserSearchSerializer

class UserSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserSearchView(generics.ListAPIView):
    """
    用户搜索视图
    支持通过用户名搜索用户，并返回分页结果
    """
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]
    pagination_class = UserSearchPagination

    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        else:
            queryset = queryset.none()  # 如果没有搜索关键词，返回空列表
            
        return queryset 