from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, SubForum, Post, Comment, Vote

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
    
    class Meta:
        model = SubForum
        fields = ('id', 'name', 'description', 'rules', 'created_by', 'created_at')
        read_only_fields = ('created_by', 'created_at')

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'format', 'author', 'created_at', 'updated_at')
        read_only_fields = ('author', 'created_at', 'updated_at')

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    reply_to_user = serializers.ReadOnlyField(source='reply_to_user.username', allow_null=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'reply_to_user', 'created_at')
        read_only_fields = ('author', 'created_at')

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