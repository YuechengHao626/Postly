from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User
from .serializers import UserLoginSerializer

class LogoutTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.logout_url = reverse('logout')
        self.login_url = reverse('login')
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123',
            email='test1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            email='test2@example.com'
        )
        
        # Login to get tokens for user1
        login_data = {
            'username': 'testuser1',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.refresh_token = response.data['refresh']
        self.access_token = response.data['access']

    def test_successful_logout(self):
        """Test successful logout with valid refresh token"""
        # Set the authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Attempt to logout
        response = self.client.post(
            self.logout_url,
            {'refresh_token': self.refresh_token},
            format='json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully logged out')
        
        # Verify that the token is blacklisted by trying to use it again
        response = self.client.post(
            self.logout_url,
            {'refresh_token': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Token is invalid or has been blacklisted')

    def test_logout_without_refresh_token(self):
        """Test logout without providing refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(
            self.logout_url,
            {},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Refresh token is required')

    def test_logout_with_invalid_refresh_token(self):
        """Test logout with invalid refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(
            self.logout_url,
            {'refresh_token': 'invalid_token'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Token is invalid or has been blacklisted')

    def test_logout_without_authentication(self):
        """Test logout without authentication"""
        response = self.client.post(
            self.logout_url,
            {'refresh_token': self.refresh_token},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_and_login_another_user(self):
        """Test logging out and then logging in as another user"""
        # First logout user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            self.logout_url,
            {'refresh_token': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Clear credentials
        self.client.credentials()
        
        # Try to login as user2
        login_data = {
            'username': 'testuser2',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Verify successful login
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['role'], self.user2.role)
        
        # Verify we can use the new token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        response = self.client.post(
            self.logout_url,
            {'refresh_token': response.data['refresh']},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_and_relogin_same_user(self):
        """Test logging out and then logging in again with the same user"""
        # First logout user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            self.logout_url,
            {'refresh_token': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Clear credentials
        self.client.credentials()
        
        # Try to login again with the same user
        login_data = {
            'username': 'testuser1',
            'password': 'testpass123'
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        
        # Verify successful login
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        self.assertEqual(login_response.data['role'], self.user1.role)
        
        # Save new tokens
        new_access_token = login_response.data['access']
        new_refresh_token = login_response.data['refresh']
        
        # Verify old token is blacklisted
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            self.logout_url,
            {'refresh_token': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify new token works
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        response = self.client.post(
            self.logout_url,
            {'refresh_token': new_refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
