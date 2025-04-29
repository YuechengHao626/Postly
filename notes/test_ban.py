from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from .models import User, SubForum, SubForumBan, ModeratorAssignment

class BanTests(TestCase):
    def setUp(self):
        # Create test users with different roles
        self.super_admin = User.objects.create_user(
            username='super_admin',
            password='testpass123',
            role='super_admin'
        )
        self.subforum_admin = User.objects.create_user(
            username='subforum_admin',
            password='testpass123',
            role='subforum_admin'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            password='testpass123',
            role='moderator'
        )
        self.normal_user = User.objects.create_user(
            username='normal_user',
            password='testpass123',
            role='user'
        )
        self.target_user = User.objects.create_user(
            username='target_user',
            password='testpass123',
            role='user'
        )

        # Create test subforum
        self.subforum = SubForum.objects.create(
            name='Test Forum',
            description='Test Description',
            created_by=self.super_admin
        )

        # Assign moderator roles
        ModeratorAssignment.objects.create(
            user=self.subforum_admin,
            sub_forum=self.subforum,
            is_admin=True,
            assigned_by=self.super_admin
        )
        ModeratorAssignment.objects.create(
            user=self.moderator,
            sub_forum=self.subforum,
            is_admin=False,
            assigned_by=self.subforum_admin
        )

        self.client = APIClient()

    def test_global_ban_by_super_admin(self):
        """Test that super admin can globally ban users"""
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(reverse('global-ban-user'), {
            'user_id': self.target_user.id,
            'action': 'ban',
            'reason': 'Test ban reason'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.is_banned)
        self.assertEqual(self.target_user.ban_reason, 'Test ban reason')
        self.assertIsNotNone(self.target_user.banned_at)

    def test_global_ban_by_non_super_admin(self):
        """Test that non-super admin cannot globally ban users"""
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(reverse('global-ban-user'), {
            'user_id': self.target_user.id,
            'action': 'ban',
            'reason': 'Test ban reason'
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.target_user.refresh_from_db()
        self.assertFalse(self.target_user.is_banned)

    def test_global_unban_by_super_admin(self):
        """Test that super admin can globally unban users"""
        # First ban the user
        self.target_user.is_banned = True
        self.target_user.ban_reason = 'Initial ban'
        self.target_user.banned_at = timezone.now()
        self.target_user.save()

        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(reverse('global-ban-user'), {
            'user_id': self.target_user.id,
            'action': 'unban'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertFalse(self.target_user.is_banned)
        self.assertIsNone(self.target_user.ban_reason)
        self.assertIsNone(self.target_user.banned_at)

    def test_subforum_ban_by_admin(self):
        """Test that subforum admin can ban users in their subforum"""
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(reverse('subforum-ban-user'), {
            'user_id': self.target_user.id,
            'subforum_id': self.subforum.id,
            'duration_days': 7,
            'reason': 'Test subforum ban'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ban = SubForumBan.objects.get(user=self.target_user, subforum=self.subforum)
        self.assertTrue(ban.is_active)
        self.assertEqual(ban.reason, 'Test subforum ban')
        self.assertGreater(ban.expires_at, timezone.now())

    def test_subforum_ban_by_moderator(self):
        """Test that moderator can ban users in their subforum"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(reverse('subforum-ban-user'), {
            'user_id': self.target_user.id,
            'subforum_id': self.subforum.id,
            'duration_days': 7,
            'reason': 'Test moderator ban'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ban = SubForumBan.objects.get(user=self.target_user, subforum=self.subforum)
        self.assertTrue(ban.is_active)

    def test_subforum_ban_by_normal_user(self):
        """Test that normal user cannot ban users"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(reverse('subforum-ban-user'), {
            'user_id': self.moderator.id,  # Try to ban a moderator
            'subforum_id': self.subforum.id,
            'duration_days': 7,
            'reason': 'Test unauthorized ban'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(SubForumBan.objects.filter(
            user=self.moderator,
            subforum=self.subforum
        ).exists())

    def test_subforum_ban_hierarchy(self):
        """Test ban hierarchy rules"""
        # Try to ban super admin with subforum admin
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(reverse('subforum-ban-user'), {
            'user_id': self.super_admin.id,
            'subforum_id': self.subforum.id,
            'duration_days': 7
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Try to ban subforum admin with moderator
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(reverse('subforum-ban-user'), {
            'user_id': self.subforum_admin.id,
            'subforum_id': self.subforum.id,
            'duration_days': 7
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subforum_unban_permissions(self):
        """Test unban permission hierarchy"""
        # Create a ban by super admin
        ban = SubForumBan.objects.create(
            user=self.target_user,
            subforum=self.subforum,
            banned_by=self.super_admin,
            reason='Super admin ban',
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True
        )

        # Try to unban with subforum admin
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(reverse('subforum-unban-user'), {
            'user_id': self.target_user.id,
            'subforum_id': self.subforum.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        ban.refresh_from_db()
        self.assertTrue(ban.is_active)

        # Unban with super admin should work
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(reverse('subforum-unban-user'), {
            'user_id': self.target_user.id,
            'subforum_id': self.subforum.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ban.refresh_from_db()
        self.assertFalse(ban.is_active)

    def test_extend_ban_duration(self):
        """Test extending ban duration"""
        # Create initial ban
        initial_expires_at = timezone.now() + timedelta(days=3)
        ban = SubForumBan.objects.create(
            user=self.target_user,
            subforum=self.subforum,
            banned_by=self.subforum_admin,
            expires_at=initial_expires_at,
            is_active=True
        )

        # Try to extend ban
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(reverse('subforum-ban-user'), {
            'user_id': self.target_user.id,
            'subforum_id': self.subforum.id,
            'duration_days': 7,
            'reason': 'Extended ban'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ban.refresh_from_db()
        self.assertGreater(ban.expires_at, initial_expires_at)

    def test_shorten_ban_duration(self):
        """Test that shorter ban duration doesn't update existing longer ban"""
        # Create initial ban
        initial_expires_at = timezone.now() + timedelta(days=7)
        ban = SubForumBan.objects.create(
            user=self.target_user,
            subforum=self.subforum,
            banned_by=self.subforum_admin,
            expires_at=initial_expires_at,
            is_active=True
        )

        # Try to shorten ban
        self.client.force_authenticate(user=self.subforum_admin)
        response = self.client.post(reverse('subforum-ban-user'), {
            'user_id': self.target_user.id,
            'subforum_id': self.subforum.id,
            'duration_days': 3,
            'reason': 'Shorter ban'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ban.refresh_from_db()
        self.assertEqual(ban.expires_at, initial_expires_at)  # Should remain unchanged 

    def test_banned_user_cannot_post(self):
        """Test that globally banned users cannot create posts"""
        # First ban the user
        self.target_user.is_banned = True
        self.target_user.ban_reason = 'Test ban'
        self.target_user.banned_at = timezone.now()
        self.target_user.save()

        # Try to create a post with banned user
        self.client.force_authenticate(user=self.target_user)
        response = self.client.post(reverse('post-list'), {
            'title': 'Test Post',
            'content': 'Test Content',
            'subforum_id': self.subforum.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('banned', response.data['detail'].lower())

    def test_subforum_banned_user_cannot_post(self):
        """Test that subforum banned users cannot post in that subforum"""
        # Create a subforum ban
        SubForumBan.objects.create(
            user=self.target_user,
            subforum=self.subforum,
            banned_by=self.subforum_admin,
            reason='Test subforum ban',
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True
        )

        # Try to create a post in the banned subforum
        self.client.force_authenticate(user=self.target_user)
        response = self.client.post(reverse('post-list'), {
            'title': 'Test Post',
            'content': 'Test Content',
            'subforum_id': self.subforum.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('you are banned from posting in this subforum', response.data['detail'].lower())

    def test_unbanned_user_can_post(self):
        """Test that user can post after being unbanned"""
        # First ban and then unban the user
        self.target_user.is_banned = True
        self.target_user.save()
        
        self.target_user.is_banned = False
        self.target_user.ban_reason = None
        self.target_user.banned_at = None
        self.target_user.save()

        # Try to create a post
        self.client.force_authenticate(user=self.target_user)
        response = self.client.post(reverse('post-list'), {
            'title': 'Test Post',
            'content': 'Test Content',
            'subforum_id': self.subforum.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_subforum_ban_does_not_affect_other_subforums(self):
        """Test that being banned in one subforum doesn't affect posting in other subforums"""
        # Create another subforum
        other_subforum = SubForum.objects.create(
            name='Other Forum',
            description='Other Description',
            created_by=self.super_admin
        )

        # Ban user in the first subforum
        SubForumBan.objects.create(
            user=self.target_user,
            subforum=self.subforum,
            banned_by=self.subforum_admin,
            reason='Test subforum ban',
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True
        )

        # Try to create a post in the other subforum
        self.client.force_authenticate(user=self.target_user)
        response = self.client.post(reverse('post-list'), {
            'title': 'Test Post',
            'content': 'Test Content',
            'subforum_id': other_subforum.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Post')

        # Verify user still cannot post in the banned subforum
        response = self.client.post(reverse('post-list'), {
            'title': 'Test Post',
            'content': 'Test Content',
            'subforum_id': self.subforum.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('you are banned from posting in this subforum', response.data['detail'].lower()) 