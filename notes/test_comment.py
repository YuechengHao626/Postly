from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import SubForum, Post, Comment, SubForumBan

User = get_user_model()

class TestComment(TestCase):
    def setUp(self):
        """测试前创建必要的数据"""
        self.client = APIClient()
        
        # 创建两个用户：发帖者和评论者
        self.post_author = User.objects.create_user(
            username='post_author',
            email='author@example.com',
            password='testpass123'
        )
        
        self.comment_user = User.objects.create_user(
            username='comment_user',
            email='commenter@example.com',
            password='testpass123'
        )

        # 创建子论坛
        self.subforum = SubForum.objects.create(
            name='Test Forum',
            description='Test Description',
            created_by=self.post_author
        )

        # 创建测试帖子
        self.test_post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            author=self.post_author,
            sub_forum=self.subforum
        )

        # 创建一个测试评论
        self.test_comment = Comment.objects.create(
            content='Test Comment',
            author=self.comment_user,
            post=self.test_post
        )

    def test_create_comment_authenticated(self):
        """测试已登录用户创建评论"""
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': self.test_post.id,
            'content': 'New Comment'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)  # 包括setUp中创建的评论
        
        # 验证评论数据
        new_comment = Comment.objects.get(content='New Comment')
        self.assertEqual(new_comment.author, self.comment_user)
        self.assertEqual(new_comment.post, self.test_post)

    def test_create_comment_with_reply(self):
        """测试创建回复其他用户的评论"""
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': self.test_post.id,
            'content': 'Reply Comment',
            'reply_to_user_id': self.post_author.id
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证回复信息
        new_comment = Comment.objects.get(content='Reply Comment')
        self.assertEqual(new_comment.reply_to_user, self.post_author)

    def test_create_comment_unauthenticated(self):
        """测试未登录用户创建评论（应该失败）"""
        data = {
            'post_id': self.test_post.id,
            'content': 'New Comment'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comment.objects.count(), 1)  # 只有setUp中创建的评论

    def test_create_comment_without_post_id(self):
        """测试创建评论时没有提供帖子ID"""
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'content': 'New Comment'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('post_id', response.data)

    def test_create_comment_invalid_post(self):
        """测试使用不存在的帖子ID创建评论"""
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': 9999,  # 不存在的ID
            'content': 'New Comment'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_post_comments(self):
        """测试获取帖子的评论列表"""
        # 再创建一个评论
        Comment.objects.create(
            content='Second Comment',
            author=self.comment_user,
            post=self.test_post
        )
        
        response = self.client.get(f'/api/posts/{self.test_post.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 应该有两个评论
        
        # 验证返回的数据格式和内容
        self.assertEqual(response.data[0]['content'], 'Test Comment')
        self.assertEqual(response.data[1]['content'], 'Second Comment')
        
        # 验证返回的字段
        comment_data = response.data[0]
        expected_fields = {'id', 'content', 'author', 'reply_to_user', 'created_at'}
        self.assertEqual(set(comment_data.keys()), expected_fields)

    def test_list_comments_nonexistent_post(self):
        """测试获取不存在的帖子的评论列表"""
        response = self.client.get('/api/posts/9999/comments/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_comment_empty_content(self):
        """测试创建空内容的评论"""
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': self.test_post.id,
            'content': ''  # 空内容
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

    def test_create_comment_invalid_reply_user(self):
        """测试使用不存在的用户ID作为回复对象"""
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': self.test_post.id,
            'content': 'New Comment',
            'reply_to_user_id': 9999  # 不存在的用户ID
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_globally_banned_user_cannot_comment(self):
        """Test that globally banned users cannot create comments"""
        # Ban the comment user
        self.comment_user.is_banned = True
        self.comment_user.ban_reason = 'Test ban'
        self.comment_user.banned_at = timezone.now()
        self.comment_user.save()

        # Try to create a comment with banned user
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': self.test_post.id,
            'content': 'Comment from banned user'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('you are banned from posting', response.data['detail'].lower())

    def test_subforum_banned_user_cannot_comment(self):
        """Test that users banned in a subforum cannot comment in that subforum"""
        # Create a subforum ban
        SubForumBan.objects.create(
            user=self.comment_user,
            subforum=self.subforum,
            banned_by=self.post_author,  # Using post_author as the banner for this test
            reason='Test subforum ban',
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True
        )

        # Try to create a comment in the banned subforum
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': self.test_post.id,
            'content': 'Comment in banned subforum'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('you are banned from posting in this subforum', response.data['detail'].lower())

    def test_subforum_ban_does_not_affect_other_subforums(self):
        """Test that being banned in one subforum doesn't affect commenting in other subforums"""
        # Create another subforum and post
        other_subforum = SubForum.objects.create(
            name='Other Forum',
            description='Other Description',
            created_by=self.post_author
        )
        other_post = Post.objects.create(
            title='Other Post',
            content='Other Content',
            author=self.post_author,
            sub_forum=other_subforum
        )

        # Ban user in the first subforum
        SubForumBan.objects.create(
            user=self.comment_user,
            subforum=self.subforum,
            banned_by=self.post_author,
            reason='Test subforum ban',
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True
        )

        # Try to comment in the other subforum
        self.client.force_authenticate(user=self.comment_user)
        data = {
            'post_id': other_post.id,
            'content': 'Comment in other subforum'
        }
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify user still cannot comment in the banned subforum
        data['post_id'] = self.test_post.id
        response = self.client.post('/api/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('you are banned from posting in this subforum', response.data['detail'].lower()) 