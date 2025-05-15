from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from ..models import User, SubForum, ModeratorAssignment
from ..serializers import SubForumSerializer

def check_admin_permission(user, subforum):
    """
    检查用户是否有权限管理该子论坛
    返回 (has_permission, is_super_admin)
    """
    if user.role == 'super_admin':
        return True, True
    
    moderator = ModeratorAssignment.objects.filter(
        user=user,
        sub_forum=subforum,
        is_admin=True
    ).first()
    
    return bool(moderator), False

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_subforums(request):
    """
    获取当前用户管理的子论坛列表
    - 超级管理员可以看到所有子论坛
    - 子论坛管理员只能看到自己管理的子论坛
    """
    if request.user.role == 'super_admin':
        subforums = SubForum.objects.all()
    else:
        subforums = SubForum.objects.filter(
            moderator_assignments__user=request.user,
            moderator_assignments__is_admin=True
        ).distinct().annotate(
            moderator_count=Count('moderator_assignments'),
            post_count=Count('posts')
        )
    
    serializer = SubForumSerializer(subforums, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_moderator(request, subforum_id):
    """
    任命版主
    - 超级管理员可以任命任何子论坛的版主
    - 子论坛管理员只能任命自己管理的子论坛的版主
    """
    subforum = get_object_or_404(SubForum, id=subforum_id)
    has_permission, is_super_admin = check_admin_permission(request.user, subforum)
    
    if not has_permission:
        return Response(
            {"detail": "You don't have permission to assign moderators"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            {"detail": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"detail": f"User with id {user_id} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # 检查是否已经是版主
    existing_assignment = ModeratorAssignment.objects.filter(
        user=target_user,
        sub_forum=subforum
    ).first()
    
    if existing_assignment:
        return Response(
            {"detail": "User is already a moderator of this subforum"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 创建版主任命
    ModeratorAssignment.objects.create(
        user=target_user,
        sub_forum=subforum,
        assigned_by=request.user,
        is_admin=False
    )
    
    return Response({"detail": "Moderator assigned successfully"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_admin(request, subforum_id):
    """
    任命子论坛管理员
    - 只有超级管理员可以任命子论坛管理员
    """
    if request.user.role != 'super_admin':
        return Response(
            {"detail": "Only super admin can assign subforum admins"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    subforum = get_object_or_404(SubForum, id=subforum_id)
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            {"detail": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"detail": f"User with id {user_id} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # 检查是否已经是管理员
    existing_assignment = ModeratorAssignment.objects.filter(
        user=target_user,
        sub_forum=subforum,
        is_admin=True
    ).first()
    
    if existing_assignment:
        return Response(
            {"detail": "User is already an admin of this subforum"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 创建管理员任命
    ModeratorAssignment.objects.create(
        user=target_user,
        sub_forum=subforum,
        assigned_by=request.user,
        is_admin=True
    )
    
    return Response({"detail": "Subforum admin assigned successfully"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_moderator(request, subforum_id):
    """
    移除版主
    - 超级管理员可以移除任何子论坛的版主
    - 子论坛管理员只能移除自己管理的子论坛的版主
    """
    subforum = get_object_or_404(SubForum, id=subforum_id)
    has_permission, is_super_admin = check_admin_permission(request.user, subforum)
    
    if not has_permission:
        return Response(
            {"detail": "You don't have permission to remove moderators"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            {"detail": "user_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"detail": f"User with id {user_id} does not exist"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # 获取版主任命记录
    assignment = ModeratorAssignment.objects.filter(
        user=target_user,
        sub_forum=subforum
    ).first()
    
    if not assignment:
        return Response(
            {"detail": "User is not a moderator of this subforum"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 检查权限
    if not is_super_admin and assignment.is_admin:
        return Response(
            {"detail": "You cannot remove a subforum admin"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    assignment.delete()
    return Response({"detail": "Moderator removed successfully"}) 