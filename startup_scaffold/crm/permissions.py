from rest_framework import permissions

class IsCustomerOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a customer or admins to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        # Otherwise, only the owner (user field) has access
        return obj.user == request.user
