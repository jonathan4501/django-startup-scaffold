from rest_framework import permissions

class IsAdminOrSelf(permissions.BasePermission):
    """
    Custom permission to only allow users to view their own attendance,
    unless they are admin/superuser.
    """

    def has_object_permission(self, request, view, obj):
        # Admins and superusers can view all
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True
        # Otherwise only allow access to own objects
        return obj.user == request.user

    def has_permission(self, request, view):
        # Allow access if user is authenticated
        return request.user and request.user.is_authenticated
