from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Otherwise, only the owner has access
        return obj == request.user

class IsWorker(permissions.BasePermission):
    """
    Custom permission to only allow users with role 'worker'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'worker'

class IsClient(permissions.BasePermission):
    """
    Custom permission to only allow users with role 'client'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'
