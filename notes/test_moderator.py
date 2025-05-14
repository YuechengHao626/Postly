from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, SubForum, ModeratorAssignment

class ModeratorTests(TestCase):
    def setUp(self):
        """测试前创建测试用户和子论坛"""
        self.client = APIClient()
        
        # 创建超级管理员
        self.super_admin = User.objects.create_user(
            username='super_admin',
            email='super_admin@example.com',
            password='testpass123',
            role='super_admin'
        )
        
        # 创建子论坛管理员
        self.subforum_admin = User.objects.create_user(
            username='subforum_admin',
            email='subforum_admin@example.com',
            password='testpass123',
            role='subforum_admin'
        )
        
        # 创建普通版主
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='testpass123',
            role='moderator'
        )
        
        # 创建普通用户
        self.normal_user = User.objects.create_user(
            username='normal_user',
            email='normal_user@example.com',
            password='testpass123',
            role='user'
        )
        
        # 创建目标用户（用于测试任命）
        self.target_user = User.objects.create_user(
            username='target_user',
            email='target_user@example.com',
            password='testpass123',
            role='user'
        )
        
        # 创建测试子论坛
        self.subforum = SubForum.objects.create(
            name='Test Forum',
            description='Test Description',
            created_by=self.super_admin
        )
        
        # 设置子论坛管理员
        ModeratorAssignment.objects.create(
            user=self.subforum_admin,
            sub_forum=self.subforum,
            assigned_by=self.super_admin,
            is_admin=True
        )

    def test_assign_moderator_by_super_admin(self):
        """测试超级管理员任命版主"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('assign-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum,
                is_admin=False
            ).exists()
        )

    def test_assign_moderator_by_subforum_admin(self):
        """测试子论坛管理员任命版主"""
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(
            reverse('assign-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum,
                is_admin=False
            ).exists()
        )

    def test_assign_moderator_by_normal_user(self):
        """测试普通用户尝试任命版主（应该失败）"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(
            reverse('assign-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum
            ).exists()
        )

    def test_assign_moderator_to_nonexistent_user(self):
        """测试任命不存在的用户为版主（应该失败）"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('assign-moderator', args=[self.subforum.id]),
            {'user_id': 99999}  # 不存在的用户ID
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_assign_moderator_without_user_id(self):
        """测试没有提供user_id时任命版主（应该失败）"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('assign-moderator', args=[self.subforum.id]),
            {}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_moderator_to_existing_moderator(self):
        """测试任命已经是版主的用户（应该失败）"""
        # 先任命为版主
        ModeratorAssignment.objects.create(
            user=self.target_user,
            sub_forum=self.subforum,
            assigned_by=self.super_admin,
            is_admin=False
        )
        
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('assign-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_admin_by_super_admin(self):
        """测试超级管理员任命子论坛管理员"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('assign-admin', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum,
                is_admin=True
            ).exists()
        )

    def test_assign_admin_by_subforum_admin(self):
        """测试子论坛管理员尝试任命管理员（应该失败）"""
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(
            reverse('assign-admin', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum,
                is_admin=True
            ).exists()
        )

    def test_assign_admin_to_existing_admin(self):
        """测试任命已经是管理员的用户（应该失败）"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('assign-admin', args=[self.subforum.id]),
            {'user_id': self.subforum_admin.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_moderator_by_super_admin(self):
        """测试超级管理员移除版主"""
        # 先任命为版主
        ModeratorAssignment.objects.create(
            user=self.target_user,
            sub_forum=self.subforum,
            assigned_by=self.super_admin,
            is_admin=False
        )
        
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('remove-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum
            ).exists()
        )

    def test_remove_moderator_by_subforum_admin(self):
        """测试子论坛管理员移除版主"""
        # 先任命为版主
        ModeratorAssignment.objects.create(
            user=self.target_user,
            sub_forum=self.subforum,
            assigned_by=self.super_admin,
            is_admin=False
        )
        
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(
            reverse('remove-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum
            ).exists()
        )

    def test_remove_moderator_by_normal_user(self):
        """测试普通用户尝试移除版主（应该失败）"""
        # 先任命为版主
        ModeratorAssignment.objects.create(
            user=self.target_user,
            sub_forum=self.subforum,
            assigned_by=self.super_admin,
            is_admin=False
        )
        
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(
            reverse('remove-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            ModeratorAssignment.objects.filter(
                user=self.target_user,
                sub_forum=self.subforum
            ).exists()
        )

    def test_remove_nonexistent_moderator(self):
        """测试移除不存在的版主（应该失败）"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('remove-moderator', args=[self.subforum.id]),
            {'user_id': self.target_user.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_admin_by_subforum_admin(self):
        """测试子论坛管理员尝试移除管理员（应该失败）"""
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(
            reverse('remove-moderator', args=[self.subforum.id]),
            {'user_id': self.subforum_admin.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            ModeratorAssignment.objects.filter(
                user=self.subforum_admin,
                sub_forum=self.subforum,
                is_admin=True
            ).exists()
        )

    def test_remove_admin_by_super_admin(self):
        """测试超级管理员移除管理员"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(
            reverse('remove-moderator', args=[self.subforum.id]),
            {'user_id': self.subforum_admin.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            ModeratorAssignment.objects.filter(
                user=self.subforum_admin,
                sub_forum=self.subforum
            ).exists()
        ) 