from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from datetime import timedelta
from .serializers import UserRegistrationSerializer, UserLoginSerializer, SubForumSerializer
from .models import User, SubForum, ModeratorAssignment

# Create your views here.

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
                refresh.set_exp(lifetime=timedelta(days=7))
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                })
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubForumViewSet(viewsets.ModelViewSet):
    """
    A viewset for SubForum that provides default operations except PATCH
    """
    queryset = SubForum.objects.all()
    serializer_class = SubForumSerializer
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']  # 移除 'patch'

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Set the creator of the subforum
        serializer.save(created_by=self.request.user)
        
        # Create a ModeratorAssignment for the creator as subforum_admin
        ModeratorAssignment.objects.create(
            user=self.request.user,
            sub_forum=serializer.instance,
            assigned_by=self.request.user,
            is_admin=True
        )
