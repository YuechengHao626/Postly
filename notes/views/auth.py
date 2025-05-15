from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, TokenBackendError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from datetime import timedelta
from ..serializers import UserRegistrationSerializer, UserLoginSerializer
from ..models import User

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                # Add custom claims
                refresh.payload.update({
                    'role': user.role,
                    'is_banned': user.is_banned,
                })
                refresh.set_exp(lifetime=timedelta(days=7))
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'role': user.role,  # Also return role in response for immediate use
                })
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # 验证token格式
                token = RefreshToken(refresh_token)
                # 将token加入黑名单
                token.blacklist()
                return Response(
                    {"message": "Successfully logged out"},
                    status=status.HTTP_200_OK
                )
            except (TokenError, InvalidToken, TokenBackendError) as e:
                # Token已经在黑名单中或无效
                return Response(
                    {"error": "Token is invalid or has been blacklisted"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response(
                {"error": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取当前登录用户的详细信息
        """
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.astimezone().isoformat(),  # 转换为本地时间
            'is_banned': user.is_banned,
        }) 