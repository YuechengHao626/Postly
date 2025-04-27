from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import SubForum, ModeratorAssignment
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class TestForum(TestCase):
    def setUp(self):
        """测试前创建测试用户"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # 创建一个测试子论坛
        self.test_forum = SubForum.objects.create(
            name='Test Forum',
            description='Test Description',
            rules='Test Rules',
            created_by=self.user
        )
        
    def test_create_forum_authenticated(self):
        """测试已登录用户创建子论坛"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Forum',
            'description': 'New Description',
            'rules': 'New Rules'
        }
        response = self.client.post('/api/subforums/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SubForum.objects.count(), 2)  # 包括setUp中创建的论坛
        self.assertEqual(SubForum.objects.get(name='New Forum').created_by, self.user)
        
        # 验证创建者是否被设置为管理员
        moderator = ModeratorAssignment.objects.get(sub_forum__name='New Forum')
        self.assertEqual(moderator.user, self.user)
        self.assertTrue(moderator.is_admin)

    def test_create_forum_unauthenticated(self):
        """测试未登录用户创建子论坛（应该失败）"""
        data = {
            'name': 'New Forum',
            'description': 'New Description',
            'rules': 'New Rules'
        }
        response = self.client.post('/api/subforums/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(SubForum.objects.count(), 1)  # 只有setUp中创建的论坛

    def test_list_forums(self):
        """测试获取子论坛列表（不需要登录）"""
        response = self.client.get('/api/subforums/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 只有setUp中创建的论坛
        self.assertEqual(response.data[0]['name'], 'Test Forum')
        self.assertEqual(response.data[0]['description'], 'Test Description')
        self.assertEqual(response.data[0]['rules'], 'Test Rules')
        self.assertEqual(response.data[0]['created_by'], 'testuser') 