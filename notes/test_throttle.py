from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, SubForum, Post
import time

class ThrottleTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # 创建测试子论坛
        self.subforum = SubForum.objects.create(
            name='Test Forum',
            description='Test Forum Description',
            created_by=self.user  # 添加创建者
        )
        
        # 创建一个测试帖子（用于评论测试）
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.user,
            sub_forum=self.subforum
        )
        
        # 设置API客户端
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # API endpoints
        self.post_url = reverse('post-list')
        self.comment_url = reverse('comment-list')

    def test_post_throttling(self):
        """测试发帖限流"""
        # 准备发帖数据
        post_data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'subforum_id': self.subforum.id
        }
        
        # 尝试发送101个请求（超过每小时100个的限制）
        responses = []
        for i in range(101):
            response = self.client.post(self.post_url, post_data, format='json')
            responses.append(response.status_code)
        
        # 验证前100个请求应该成功
        self.assertEqual(responses[:100].count(status.HTTP_201_CREATED), 100)
        # 第101个请求应该被限流
        self.assertEqual(responses[100], status.HTTP_429_TOO_MANY_REQUESTS)

    def test_comment_throttling(self):
        """测试评论限流"""
        # 准备评论数据
        comment_data = {
            'content': 'Test Comment',
            'post_id': self.post.id
        }
        
        # 尝试发送1001个请求（超过每小时1000个的限制）
        responses = []
        for i in range(1001):
            response = self.client.post(self.comment_url, comment_data, format='json')
            responses.append(response.status_code)
        
        # 验证前1000个请求应该成功
        self.assertEqual(responses[:1000].count(status.HTTP_201_CREATED), 1000)
        # 第1001个请求应该被限流
        self.assertEqual(responses[1000], status.HTTP_429_TOO_MANY_REQUESTS)

   