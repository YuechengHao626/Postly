from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, SubForum, Post, Comment, Vote, SubForumBan

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class SubForumSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    moderator_count = serializers.IntegerField(read_only=True)
    post_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SubForum
        fields = ('id', 'name', 'description', 'rules', 'created_by', 'created_at', 'moderator_count', 'post_count')
        read_only_fields = ('created_by', 'created_at', 'moderator_count', 'post_count')

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    sub_forum = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'format', 'author', 'sub_forum', 'created_at', 'updated_at')
        read_only_fields = ('author', 'created_at', 'updated_at')
    
    def get_sub_forum(self, obj):
        return {
            'id': obj.sub_forum.id,
            'name': obj.sub_forum.name
        }

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    reply_to_user = serializers.ReadOnlyField(source='reply_to_user.username', allow_null=True)
    post = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'reply_to_user', 'post', 'created_at')
        read_only_fields = ('author', 'created_at')

    def get_post(self, obj):
        return {
            'id': obj.post.id,
            'title': obj.post.title,
            'sub_forum': {
                'id': obj.post.sub_forum.id,
                'name': obj.post.sub_forum.name
            }
        }

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'user', 'target_type', 'target_id', 'value', 'created_at']
        read_only_fields = ['user', 'value', 'created_at']

    def validate_target_type(self, value):
        if value not in ['post', 'comment']:
            raise serializers.ValidationError("Invalid target type. Must be either 'post' or 'comment'.")
        return value

    def create(self, validated_data):
        # Force value to be 'like'
        validated_data['value'] = 'like'
        return super().create(validated_data)

class GlobalBanSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['ban', 'unban'])
    reason = serializers.CharField(required=False, allow_blank=True)

class SubForumBanSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    subforum_id = serializers.IntegerField()
    duration_days = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """
        Validate data and check role hierarchy
        """
        try:
            target_user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Target user not found")

        try:
            SubForum.objects.get(id=data['subforum_id'])
        except SubForum.DoesNotExist:
            raise serializers.ValidationError("Subforum not found")

        # Check role hierarchy
        request = self.context.get('request')
        if request and request.user:
            role_hierarchy = {
                'user': 0,
                'moderator': 1,
                'subforum_admin': 2,
                'super_admin': 3
            }
            banner_role = role_hierarchy.get(request.user.role, 0)
            target_role = role_hierarchy.get(target_user.role, 0)

            if banner_role <= target_role:
                raise serializers.ValidationError(
                    "You cannot ban users with equal or higher privileges"
                )

        return data

class SubForumBanDetailSerializer(serializers.ModelSerializer):
    banned_by_username = serializers.CharField(source='banned_by.username', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SubForumBan
        fields = ['id', 'user', 'user_username', 'subforum', 'banned_by', 
                 'banned_by_username', 'reason', 'is_active', 'created_at', 
                 'expires_at']
        read_only_fields = ['id', 'created_at']

class PostSearchSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    sub_forum_name = serializers.ReadOnlyField(source='sub_forum.name')
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'sub_forum_name', 'created_at', 'updated_at')

class SubForumSearchSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SubForum
        fields = ('id', 'name', 'description', 'created_by', 'created_at', 'post_count')
    
    def get_post_count(self, obj):
        return obj.posts.count()

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'created_at']
        read_only_fields = fields  # 所有字段都是只读的 