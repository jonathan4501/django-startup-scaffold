from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp', 'is_read', 'read_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

class ConversationSerializer(serializers.ModelSerializer):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'owner', 'participants', 'created_at', 'last_message', 'last_updated']

    def create(self, validated_data):
        participants_data = validated_data.pop('participants', [])
        validated_data['owner'] = self.context['request'].user
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants_data)
        # Add owner as participant
        conversation.participants.add(self.context['request'].user)
        return conversation
