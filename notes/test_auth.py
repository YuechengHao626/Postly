from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from .models import User
import json

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        
        # Create test users with different roles
        self.normal_user = User.objects.create_user(
            username='normal_user',
            password='testpass123',
            role='user'
        )
        
        self.moderator_user = User.objects.create_user(
            username='moderator_user',
            password='testpass123',
            role='moderator'
        )
        
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='testpass123',
            role='super_admin'
        )

    def test_user_login_with_role(self):
        # Test normal user login
        response = self.client.post(self.login_url, {
            'username': 'normal_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['role'], 'user')
        
        # Verify token contains role information
        access_token = response.data['access']
        token_obj = AccessToken(access_token)
        self.assertEqual(token_obj.payload['role'], 'user')
        self.assertEqual(token_obj.payload['is_banned'], False)

    def test_moderator_login_with_role(self):
        response = self.client.post(self.login_url, {
            'username': 'moderator_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'moderator')
        
        access_token = response.data['access']
        token_obj = AccessToken(access_token)
        self.assertEqual(token_obj.payload['role'], 'moderator')

    def test_admin_login_with_role(self):
        response = self.client.post(self.login_url, {
            'username': 'admin_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'super_admin')
        
        access_token = response.data['access']
        token_obj = AccessToken(access_token)
        self.assertEqual(token_obj.payload['role'], 'super_admin')

    def test_banned_user_login(self):
        # Ban the normal user
        self.normal_user.is_banned = True
        self.normal_user.save()
        
        response = self.client.post(self.login_url, {
            'username': 'normal_user',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        access_token = response.data['access']
        token_obj = AccessToken(access_token)
        self.assertTrue(token_obj.payload['is_banned'])

    def test_invalid_login(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistent_user',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 