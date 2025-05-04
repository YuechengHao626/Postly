from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, SubForum, Post
from django.utils import timezone

class SearchTests(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        
        # 创建测试子论坛
        self.subforum1 = SubForum.objects.create(
            name='Python技术讨论',
            description='关于Python编程的讨论',
            created_by=self.user
        )
        self.subforum2 = SubForum.objects.create(
            name='Java开发',
            description='Java技术交流',
            created_by=self.user
        )
        
        # 创建测试帖子
        self.post1 = Post.objects.create(
            title='Python基础教程',
            content='这是一个Python入门教程',
            author=self.user,
            sub_forum=self.subforum1
        )
        self.post2 = Post.objects.create(
            title='Java面试题',
            content='常见的Java面试问题',
            author=self.user,
            sub_forum=self.subforum2
        )
        self.post3 = Post.objects.create(
            title='Python高级技巧',
            content='Python进阶编程技巧分享',
            author=self.user,
            sub_forum=self.subforum1
        )

    def test_post_search_with_title(self):
        """测试通过标题搜索帖子"""
        url = reverse('post-search')
        response = self.client.get(url, {'q': 'Python'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(len(response.data['results']), 2)
        titles = [post['title'] for post in response.data['results']]
        self.assertTrue('Python基础教程' in titles)
        self.assertTrue('Python高级技巧' in titles)

    def test_post_search_with_content(self):
        """测试通过内容搜索帖子"""
        url = reverse('post-search')
        response = self.client.get(url, {'q': '面试'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Java面试题')

    def test_post_search_no_results(self):
        """测试搜索不存在的帖子"""
        url = reverse('post-search')
        response = self.client.get(url, {'q': '不存在的内容'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_post_search_empty_query(self):
        """测试空搜索查询"""
        url = reverse('post-search')
        response = self.client.get(url, {'q': ''})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Search query is required')

    def test_post_search_pagination(self):
        """测试帖子搜索分页"""
        # 创建额外的测试帖子
        for i in range(15):
            Post.objects.create(
                title=f'Python测试帖子{i}',
                content=f'测试内容{i}',
                author=self.user,
                sub_forum=self.subforum1
            )
        
        url = reverse('post-search')
        response = self.client.get(url, {'q': 'Python', 'page': 1, 'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 17)  # 15 + 2 from setUp
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['page'], 1)
        self.assertEqual(response.data['page_size'], 10)

    def test_subforum_search_with_name(self):
        """测试通过名称搜索子论坛"""
        url = reverse('subforum-search')
        response = self.client.get(url, {'q': 'Python'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Python技术讨论')

    def test_subforum_search_with_description(self):
        """测试通过描述搜索子论坛"""
        url = reverse('subforum-search')
        response = self.client.get(url, {'q': '技术'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 2)
        names = [forum['name'] for forum in response.data['results']]
        self.assertTrue('Python技术讨论' in names)
        self.assertTrue('Java开发' in names)

    def test_subforum_search_post_count(self):
        """测试子论坛搜索结果中的帖子计数"""
        url = reverse('subforum-search')
        response = self.client.get(url, {'q': 'Python'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['post_count'], 2)

    def test_subforum_search_empty_query(self):
        """测试空搜索查询"""
        url = reverse('subforum-search')
        response = self.client.get(url, {'q': ''})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Search query is required') 