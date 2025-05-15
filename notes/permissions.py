from rest_framework import permissions

class IsSubForumAdminOrSuperAdmin(permissions.BasePermission):
    """
    允许子论坛管理员或超级管理员访问
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['subforum_admin', 'super_admin']

class IsModeratorOrHigher(permissions.BasePermission):
    """
    允许版主或更高权限的用户访问
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['moderator', 'subforum_admin', 'super_admin']

class IsSuperAdmin(permissions.BasePermission):
    """
    只允许超级管理员访问
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'super_admin'

class IsPostAuthorOrModeratorOrHigher(permissions.BasePermission):
    """
    允许帖子作者、版主或更高权限的用户访问
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 帖子作者可以访问
        if obj.author == request.user:
            return True
        
        # 版主或更高权限的用户可以访问
        if request.user.role in ['moderator', 'subforum_admin', 'super_admin']:
            # 如果是版主，检查是否是该子论坛的版主
            if request.user.role == 'moderator':
                return obj.sub_forum.moderator_assignments.filter(
                    user=request.user,
                    is_active=True
                ).exists()
            return True
        
        return False

class IsCommentAuthorOrModeratorOrHigher(permissions.BasePermission):
    """
    允许评论作者、版主或更高权限的用户访问
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # 评论作者可以访问
        if obj.author == request.user:
            return True
        
        # 版主或更高权限的用户可以访问
        if request.user.role in ['moderator', 'subforum_admin', 'super_admin']:
            # 如果是版主，检查是否是该子论坛的版主
            if request.user.role == 'moderator':
                return obj.post.sub_forum.moderator_assignments.filter(
                    user=request.user,
                    is_active=True
                ).exists()
            return True
        
        return False

class IsNotBanned(permissions.BasePermission):
    """
    检查用户是否被禁止
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
        return not request.user.is_banned

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return True
        
        # 检查全局禁止状态
        if request.user.is_banned:
            return False
        
        # 检查子论坛禁止状态
        if hasattr(obj, 'sub_forum'):
            subforum = obj.sub_forum
        elif hasattr(obj, 'post'):
            subforum = obj.post.sub_forum
        else:
            return True
        
        return not request.user.is_banned_in_subforum(subforum) 