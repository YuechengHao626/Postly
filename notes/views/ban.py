from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta

from ..models import User, SubForum, SubForumBan, ModeratorAssignment
from ..serializers import GlobalBanSerializer, SubForumBanSerializer, SubForumBanDetailSerializer

def check_ban_permission(user, subforum):
    """
    Check if user has permission to ban in the given subforum
    Returns (has_permission, is_super_admin, is_subforum_admin)
    """
    if user.role == 'super_admin':
        return True, True, False
    
    moderator = ModeratorAssignment.objects.filter(
        user=user,
        sub_forum=subforum
    ).first()
    
    if moderator and moderator.is_admin:
        return True, False, True
    elif moderator:
        return True, False, False
    
    return False, False, False

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def global_ban_user(request):
    """
    Global ban/unban a user (super admin only)
    """
    if request.user.role != 'super_admin':
        return Response(
            {"detail": "Only super admins can perform global bans"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = GlobalBanSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    target_user = get_object_or_404(User, id=serializer.validated_data['user_id'])
    action = serializer.validated_data['action']
    reason = serializer.validated_data.get('reason', '')

    if target_user.role == 'super_admin':
        return Response(
            {"detail": "Cannot ban super admins"},
            status=status.HTTP_403_FORBIDDEN
        )

    if action == 'ban':
        target_user.is_banned = True
        target_user.ban_reason = reason
        target_user.banned_at = timezone.now()
    else:  # unban
        target_user.is_banned = False
        target_user.ban_reason = None
        target_user.banned_at = None

    target_user.save()

    return Response({
        "detail": f"User has been {'banned' if action == 'ban' else 'unbanned'} successfully"
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subforum_ban_user(request):
    """
    Ban a user in a specific subforum
    """
    serializer = SubForumBanSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    subforum = get_object_or_404(SubForum, id=data['subforum_id'])
    target_user = get_object_or_404(User, id=data['user_id'])

    # Check permissions
    has_permission, is_super, is_admin = check_ban_permission(request.user, subforum)
    if not has_permission:
        return Response(
            {"detail": "You don't have permission to ban users in this subforum"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Calculate expiration time
    expires_at = timezone.now() + timedelta(days=data['duration_days'])

    # Get or create ban record
    ban_record, created = SubForumBan.objects.get_or_create(
        user=target_user,
        subforum=subforum,
        defaults={
            'banned_by': request.user,
            'reason': data.get('reason', ''),
            'expires_at': expires_at,
            'is_active': True
        }
    )

    if not created:
        # Check if the banner has permission to modify this ban
        if not is_super:  # Not a super admin
            if ban_record.banned_by.role == 'super_admin':
                return Response(
                    {"detail": "Cannot modify a ban placed by a super admin"},
                    status=status.HTTP_403_FORBIDDEN
                )
            if not is_admin and ban_record.banned_by.role == 'subforum_admin':
                return Response(
                    {"detail": "Cannot modify a ban placed by a subforum admin"},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Only update if new expiration is later
        if expires_at > ban_record.expires_at:
            ban_record.expires_at = expires_at
            ban_record.reason = data.get('reason', ban_record.reason)
            ban_record.banned_by = request.user
            ban_record.is_active = True
            ban_record.save()

    serializer = SubForumBanDetailSerializer(ban_record)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subforum_unban_user(request):
    """
    Unban a user from a specific subforum
    """
    user_id = request.data.get('user_id')
    subforum_id = request.data.get('subforum_id')

    if not user_id or not subforum_id:
        return Response(
            {"detail": "Both user_id and subforum_id are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    subforum = get_object_or_404(SubForum, id=subforum_id)
    ban_record = get_object_or_404(
        SubForumBan,
        user_id=user_id,
        subforum_id=subforum_id,
        is_active=True
    )

    # Check permissions
    has_permission, is_super, is_admin = check_ban_permission(request.user, subforum)
    if not has_permission:
        return Response(
            {"detail": "You don't have permission to unban users in this subforum"},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if the unbanner has permission to remove this ban
    if not is_super:  # Not a super admin
        if ban_record.banned_by.role == 'super_admin':
            return Response(
                {"detail": "Cannot remove a ban placed by a super admin"},
                status=status.HTTP_403_FORBIDDEN
            )
        if not is_admin and ban_record.banned_by.role == 'subforum_admin':
            return Response(
                {"detail": "Cannot remove a ban placed by a subforum admin"},
                status=status.HTTP_403_FORBIDDEN
            )

    ban_record.is_active = False
    ban_record.save()

    return Response({
        "detail": "User has been unbanned from the subforum successfully"
    }) 