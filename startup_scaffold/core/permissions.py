from rest_framework import permissions
from messaging.models import Conversation, Message

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the admin user.
        return request.user and request.user.is_staff

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        # Modified to support 'client' attribute for Job model
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'client'):
            return obj.client == request.user
        return False

class IsParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it or its messages.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if isinstance(obj, Conversation):
            return user in obj.participants.all() or user == obj.owner
        elif isinstance(obj, Message):
            return user in obj.conversation.participants.all() or user == obj.conversation.owner
        return False

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # For list views, we allow access; filtering will be done in the viewsets' get_queryset
        return True
