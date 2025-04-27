from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import SubForum, ModeratorAssignment, Post
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class TestForum(TestCase):
    def setUp(self):
        """测试前创建测试用户和论坛"""
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
        
        # 创建一个测试帖子
        self.test_post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            format='markdown',
            author=self.user,
            sub_forum=self.test_forum
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

    def test_create_post_authenticated(self):
        """测试已登录用户创建帖子"""
        self.client.force_authenticate(user=self.user)
        data = {
            'subforum_id': self.test_forum.id,
            'title': 'New Post',
            'content': 'New Content',
            'format': 'markdown'
        }
        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)  # 包括setUp中创建的帖子
        
        # 验证帖子数据
        new_post = Post.objects.get(title='New Post')
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.sub_forum, self.test_forum)
        self.assertEqual(new_post.content, 'New Content')

    def test_create_post_unauthenticated(self):
        """测试未登录用户创建帖子（应该失败）"""
        data = {
            'subforum_id': self.test_forum.id,
            'title': 'New Post',
            'content': 'New Content',
            'format': 'markdown'
        }
        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.count(), 1)  # 只有setUp中创建的帖子

    def test_create_post_without_subforum_id(self):
        """测试创建帖子时没有提供子论坛ID"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Post',
            'content': 'New Content',
            'format': 'markdown'
        }
        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('subforum_id', response.data)

    def test_create_post_invalid_subforum(self):
        """测试使用不存在的子论坛ID创建帖子"""
        self.client.force_authenticate(user=self.user)
        data = {
            'subforum_id': 9999,  # 不存在的ID
            'title': 'New Post',
            'content': 'New Content',
            'format': 'markdown'
        }
        response = self.client.post('/api/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_subforum_posts(self):
        """测试获取子论坛的帖子列表"""
        # 再创建一个帖子
        Post.objects.create(
            title='Second Post',
            content='Second Content',
            format='markdown',
            author=self.user,
            sub_forum=self.test_forum
        )
        
        response = self.client.get(f'/api/subforums/{self.test_forum.id}/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 应该有两个帖子
        
        # 验证返回的数据格式和内容
        self.assertEqual(response.data[0]['title'], 'Second Post')  # 最新的帖子应该在前面
        self.assertEqual(response.data[1]['title'], 'Test Post')
        
        # 验证返回的字段
        post_data = response.data[0]
        expected_fields = {'id', 'title', 'content', 'format', 'author', 'created_at', 'updated_at'}
        self.assertEqual(set(post_data.keys()), expected_fields)

    def test_list_posts_nonexistent_subforum(self):
        """测试获取不存在的子论坛的帖子列表"""
        response = self.client.get('/api/subforums/9999/posts/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 