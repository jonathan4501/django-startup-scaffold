from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.utils import timezone
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from core.permissions import IsParticipant

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        user = self.request.user
        return Conversation.objects.filter(Q(participants=user) | Q(owner=user)).distinct()

    def retrieve(self, request, *args, **kwargs):
        # Get the conversation from all conversations, not just user's conversations
        try:
            conversation = Conversation.objects.get(pk=kwargs['pk'])
        except Conversation.DoesNotExist:
            raise NotFound("Conversation not found.")
        
        # Check if user is participant
        if not (request.user in conversation.participants.all() or request.user == conversation.owner):
            raise PermissionDenied("You do not have permission to access this conversation.")
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Ensure title is present
        if 'title' not in serializer.validated_data:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"title": "Title is required"})
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user:
            return Response(
                {"detail": "Only the owner can update the conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    filter_backends = [filters.SearchFilter]
    search_fields = ['content']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Message.objects.none()
        user = self.request.user
        return Message.objects.filter(
            Q(conversation__participants=user) | Q(conversation__owner=user)
        ).distinct()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not (request.user in instance.conversation.participants.all() or request.user == instance.conversation.owner):
                raise PermissionDenied("You do not have permission to access this message.")
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Message.DoesNotExist:
            raise NotFound("Message not found.")

    def perform_create(self, serializer):
        # Check if user is participant of the conversation
        conversation = serializer.validated_data['conversation']
        user = self.request.user
        if not (user in conversation.participants.all() or user == conversation.owner):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be a participant of the conversation to send messages.")
        
        message = serializer.save()
        # Update last_message and last_updated in Conversation
        conversation.last_message = message.content
        conversation.last_updated = timezone.now()
        conversation.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender != request.user and not request.data.get('is_read', False):
            return Response(
                {"detail": "Only the sender can update the message content."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
