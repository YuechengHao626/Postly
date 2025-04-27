from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Post, Comment, Vote, SubForum

class VoteTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        # Create a subforum
        self.subforum = SubForum.objects.create(
            name='Test Forum',
            description='Test Forum Description',
            created_by=self.user
        )

        # Create a test post
        self.post = Post.objects.create(
            sub_forum=self.subforum,
            author=self.user,
            title='Test Post',
            content='Test Content'
        )

        # Create a test comment
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test Comment'
        )

        # URL for creating votes
        self.vote_url = reverse('vote-create')

    def test_create_post_vote_authenticated(self):
        """
        Test that an authenticated user can create a vote for a post
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'target_type': 'post',
            'target_id': self.post.id
        }
        response = self.client.post(self.vote_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().value, 'like')

    def test_create_comment_vote_authenticated(self):
        """
        Test that an authenticated user can create a vote for a comment
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'target_type': 'comment',
            'target_id': self.comment.id
        }
        response = self.client.post(self.vote_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().value, 'like')

    def test_vote_unauthenticated(self):
        """
        Test that an unauthenticated user cannot create a vote
        """
        data = {
            'target_type': 'post',
            'target_id': self.post.id
        }
        response = self.client.post(self.vote_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Vote.objects.count(), 0)

    def test_vote_idempotency(self):
        """
        Test that voting multiple times by the same user only creates one vote
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'target_type': 'post',
            'target_id': self.post.id
        }
        
        # First vote
        response1 = self.client.post(self.vote_url, data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second vote (should be idempotent)
        response2 = self.client.post(self.vote_url, data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Check that only one vote exists
        self.assertEqual(Vote.objects.count(), 1)

    def test_invalid_target_type(self):
        """
        Test that invalid target_type is rejected
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'target_type': 'invalid',
            'target_id': self.post.id
        }
        response = self.client.post(self.vote_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 0)

    def test_nonexistent_target_id(self):
        """
        Test voting for a nonexistent target_id
        """
        self.client.force_authenticate(user=self.user)
        data = {
            'target_type': 'post',
            'target_id': 99999  # Non-existent ID
        }
        response = self.client.post(self.vote_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 0) 