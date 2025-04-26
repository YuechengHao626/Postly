from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('subforum_admin', 'Subforum Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        null=False
    )
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(null=True, blank=True)
    banned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=False)

    class Meta:
        db_table = 'users'

class SubForum(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(null=True, blank=True)
    rules = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_subforums',
        null=False
    )
    created_at = models.DateTimeField(default=timezone.now, null=False)

    class Meta:
        db_table = 'sub_forums'

class ModeratorAssignment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='moderator_assignments',
        null=False
    )
    sub_forum = models.ForeignKey(
        SubForum,
        on_delete=models.CASCADE,
        related_name='moderator_assignments',
        null=False
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_moderators',
        null=True
    )
    is_admin = models.BooleanField(default=False, null=False)
    created_at = models.DateTimeField(default=timezone.now, null=False)

    class Meta:
        db_table = 'moderator_assignments'
        unique_together = ('user', 'sub_forum')

class Post(models.Model):
    FORMAT_CHOICES = [
        ('markdown', 'Markdown'),
        ('wysiwyg', 'WYSIWYG'),
    ]

    sub_forum = models.ForeignKey(
        SubForum,
        on_delete=models.CASCADE,
        related_name='posts',
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        null=False
    )
    title = models.CharField(max_length=255, null=False)
    content = models.TextField(null=False)
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='markdown',
        null=False
    )
    created_at = models.DateTimeField(default=timezone.now, null=False)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # 检查是否是更新操作
        if self.pk:  # 如果存在pk，说明是更新操作
            # 获取原始对象
            original = Post.objects.get(pk=self.pk)
            # 只有当内容发生变化时才更新updated_at
            if original.content != self.content:
                self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'posts'

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        null=False
    )
    reply_to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='replied_comments',
        null=True
    )
    content = models.TextField(null=False)
    created_at = models.DateTimeField(default=timezone.now, null=False)

    def save(self, *args, **kwargs):
        # 如果是新评论，更新帖子的updated_at
        if not self.pk:
            self.post.updated_at = timezone.now()
            self.post.save(update_fields=['updated_at'])
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'comments'

class Vote(models.Model):
    TARGET_TYPE_CHOICES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
    ]
    VALUE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        null=False
    )
    target_type = models.CharField(
        max_length=10,
        choices=TARGET_TYPE_CHOICES,
        null=False
    )
    target_id = models.IntegerField(null=False)
    value = models.CharField(
        max_length=10,
        choices=VALUE_CHOICES,
        null=False
    )
    created_at = models.DateTimeField(default=timezone.now, null=False)

    class Meta:
        db_table = 'votes'
        unique_together = ('user', 'target_type', 'target_id')
