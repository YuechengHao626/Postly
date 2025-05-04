from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'created_at']
        read_only_fields = fields  # 所有字段都是只读的 