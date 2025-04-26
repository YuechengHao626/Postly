from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import SubForum, ModeratorAssignment, Post, Comment, Vote
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'user')
        self.assertFalse(self.user.is_banned)
        self.assertIsNone(self.user.ban_reason)
        self.assertIsNone(self.user.banned_at)
        self.assertIsNotNone(self.user.created_at)

    def test_user_ban(self):
        self.user.is_banned = True
        self.user.ban_reason = 'Test ban'
        self.user.banned_at = timezone.now()
        self.user.save()
        
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.is_banned)
        self.assertEqual(user.ban_reason, 'Test ban')
        self.assertIsNotNone(user.banned_at)

class SubForumModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123'
        )
        self.subforum = SubForum.objects.create(
            name='Test Subforum',
            description='Test Description',
            rules='Test Rules',
            created_by=self.user
        )

    def test_subforum_creation(self):
        self.assertEqual(self.subforum.name, 'Test Subforum')
        self.assertEqual(self.subforum.description, 'Test Description')
        self.assertEqual(self.subforum.rules, 'Test Rules')
        self.assertEqual(self.subforum.created_by, self.user)
        self.assertIsNotNone(self.subforum.created_at)

    def test_subforum_unique_name(self):
        with self.assertRaises(Exception):
            SubForum.objects.create(
                name='Test Subforum',  # Same name
                created_by=self.user
            )

class ModeratorAssignmentModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123'
        )
        self.subforum = SubForum.objects.create(
            name='Test Subforum',
            created_by=self.admin
        )
        self.assignment = ModeratorAssignment.objects.create(
            user=self.moderator,
            sub_forum=self.subforum,
            assigned_by=self.admin,
            is_admin=False
        )

    def test_moderator_assignment_creation(self):
        self.assertEqual(self.assignment.user, self.moderator)
        self.assertEqual(self.assignment.sub_forum, self.subforum)
        self.assertEqual(self.assignment.assigned_by, self.admin)
        self.assertFalse(self.assignment.is_admin)
        self.assertIsNotNone(self.assignment.created_at)

    def test_unique_moderator_per_subforum(self):
        with self.assertRaises(Exception):
            ModeratorAssignment.objects.create(
                user=self.moderator,
                sub_forum=self.subforum,
                assigned_by=self.admin
            )

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='testpass123'
        )
        self.subforum = SubForum.objects.create(
            name='Test Subforum',
            created_by=self.user
        )
        self.post = Post.objects.create(
            sub_forum=self.subforum,
            author=self.user,
            title='Test Post',
            content='Test Content',
            format='markdown'
        )

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'Test Content')
        self.assertEqual(self.post.format, 'markdown')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.sub_forum, self.subforum)
        self.assertIsNotNone(self.post.created_at)

    def test_post_update(self):
        self.post.title = 'Updated Title'
        self.post.save()
        self.assertEqual(self.post.title, 'Updated Title')

class CommentModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='testpass123'
        )
        self.reply_to = User.objects.create_user(
            username='replyto',
            email='replyto@example.com',
            password='testpass123'
        )
        self.subforum = SubForum.objects.create(
            name='Test Subforum',
            created_by=self.author
        )
        self.post = Post.objects.create(
            sub_forum=self.subforum,
            author=self.author,
            title='Test Post',
            content='Test Content'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.author,
            reply_to_user=self.reply_to,
            content='Test Comment'
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.content, 'Test Comment')
        self.assertEqual(self.comment.author, self.author)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.reply_to_user, self.reply_to)
        self.assertIsNotNone(self.comment.created_at)

class VoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='voter',
            email='voter@example.com',
            password='testpass123'
        )
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='testpass123'
        )
        self.subforum = SubForum.objects.create(
            name='Test Subforum',
            created_by=self.author
        )
        self.post = Post.objects.create(
            sub_forum=self.subforum,
            author=self.author,
            title='Test Post',
            content='Test Content'
        )
        self.vote = Vote.objects.create(
            user=self.user,
            target_type='post',
            target_id=self.post.id,
            value='like'
        )

    def test_vote_creation(self):
        self.assertEqual(self.vote.user, self.user)
        self.assertEqual(self.vote.target_type, 'post')
        self.assertEqual(self.vote.target_id, self.post.id)
        self.assertEqual(self.vote.value, 'like')
        self.assertIsNotNone(self.vote.created_at)

    def test_unique_vote_per_target(self):
        with self.assertRaises(Exception):
            Vote.objects.create(
                user=self.user,
                target_type='post',
                target_id=self.post.id,
                value='dislike'
            )

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }

    def test_user_registration(self):
        """测试用户注册功能"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created successfully')
        
        # 验证用户是否被正确创建
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'user')  # 验证默认角色是user
        self.assertTrue(user.check_password('testpass123'))

    def test_user_registration_with_mismatched_passwords(self):
        """测试密码不匹配的注册"""
        data = self.user_data.copy()
        data['password2'] = 'differentpass'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_login(self):
        """测试用户登录功能"""
        # 先创建用户
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_with_wrong_credentials(self):
        """测试使用错误凭据登录"""
        login_data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_user_registration_with_existing_username(self):
        """测试使用已存在的用户名注册"""
        # 先创建一个用户
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_with_invalid_email(self):
        """测试使用无效邮箱注册"""
        data = self.user_data.copy()
        data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_password_hashing(self):
        """测试密码是否正确加密存储"""
        # 创建用户
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 获取用户对象
        user = User.objects.get(username='testuser')
        
        # 验证密码已被加密（不是明文存储）
        self.assertNotEqual(user.password, 'testpass123')
        
        # 验证密码是否使用了Django的默认哈希算法（通常以 'pbkdf2_sha256$' 开头）
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        
        # 验证密码长度（加密后的密码应该很长）
        self.assertGreater(len(user.password), 50)
        
        # 验证原始密码仍然可以通过验证
        self.assertTrue(user.check_password('testpass123'))
        
        # 验证错误的密码不能通过验证
        self.assertFalse(user.check_password('wrongpassword'))
