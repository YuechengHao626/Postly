from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class UserSearchAPITests(APITestCase):
    def setUp(self):
        # 创建测试用户数据
        self.user1 = User.objects.create_user(
            username='john_doe',
            password='test123',
            role='user',
            created_at=timezone.now() - timedelta(days=2)
        )
        self.user2 = User.objects.create_user(
            username='john_smith',
            password='test123',
            role='moderator',
            created_at=timezone.now() - timedelta(days=1)
        )
        self.user3 = User.objects.create_user(
            username='jane_doe',
            password='test123',
            role='user',
            created_at=timezone.now()
        )
        
        self.search_url = reverse('user-search')

    def test_search_with_valid_query(self):
        """测试有效的搜索查询"""
        response = self.client.get(f'{self.search_url}?q=john')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # 应该找到2个用户
        self.assertEqual(response.data['results'][0]['username'], 'john_smith')  # 按创建时间降序排序

    def test_search_case_insensitive(self):
        """测试大小写不敏感搜索"""
        response = self.client.get(f'{self.search_url}?q=JOHN')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_empty_search_query(self):
        """测试空搜索查询"""
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_pagination(self):
        """测试分页功能"""
        # 创建额外的用户以测试分页
        for i in range(15):
            User.objects.create_user(
                username=f'test_user_{i}',
                password='test123',
                role='user',
                created_at=timezone.now()
            )
        
        # 测试第一页
        response = self.client.get(f'{self.search_url}?q=test_user')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # 默认每页10条
        self.assertIsNotNone(response.data['next'])  # 应该有下一页
        self.assertIsNone(response.data['previous'])  # 第一页没有上一页

        # 测试第二页
        response = self.client.get(f'{self.search_url}?q=test_user&page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # 第二页应该有5条
        self.assertIsNone(response.data['next'])  # 最后一页没有下一页
        self.assertIsNotNone(response.data['previous'])  # 应该有上一页

    def test_search_no_results(self):
        """测试没有匹配结果的搜索"""
        response = self.client.get(f'{self.search_url}?q=nonexistent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_response_fields(self):
        """测试响应中包含所需的字段"""
        response = self.client.get(f'{self.search_url}?q=john')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data['results'][0]
        
        # 验证返回的字段
        expected_fields = {'id', 'username', 'role', 'created_at'}
        self.assertEqual(set(user_data.keys()), expected_fields)
        
        # 验证不包含敏感信息
        self.assertNotIn('password', user_data)
        self.assertNotIn('email', user_data) 