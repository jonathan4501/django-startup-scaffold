from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()

class ConversationModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPass123!'
        )
        self.user3 = User.objects.create_user(
            email='user3@example.com',
            password='TestPass123!'
        )

    def test_conversation_creation(self):
        """Test conversation model creation"""
        conversation = Conversation.objects.create(
            owner=self.user1,
            title='Test Conversation'
        )
        conversation.participants.add(self.user1, self.user2)
        
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertEqual(conversation.owner, self.user1)
        self.assertEqual(conversation.participants.count(), 2)
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())

    def test_conversation_str_method(self):
        """Test conversation string representation"""
        conversation = Conversation.objects.create(
            owner=self.user1,
            title='Test Conversation'
        )
        self.assertEqual(str(conversation), 'Test Conversation')

class MessageModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPass123!'
        )
        self.conversation = Conversation.objects.create(
            owner=self.user1,
            title='Test Conversation'
        )
        self.conversation.participants.add(self.user1, self.user2)

    def test_message_creation(self):
        """Test message model creation"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, this is a test message!'
        )
        
        self.assertEqual(message.conversation, self.conversation)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.content, 'Hello, this is a test message!')
        self.assertFalse(message.is_read)

    def test_message_str_method(self):
        """Test message string representation"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, this is a test message!'
        )
        expected_str = f"Message from {self.user1.email} in {self.conversation.title}"
        self.assertEqual(str(message), expected_str)

class ConversationAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPass123!'
        )
        self.user3 = User.objects.create_user(
            email='user3@example.com',
            password='TestPass123!'
        )
        
        self.conversation = Conversation.objects.create(
            owner=self.user1,
            title='Test Conversation'
        )
        self.conversation.participants.add(self.user1, self.user2)
        
        self.conversation_list_url = reverse('conversation-list')
        self.conversation_detail_url = reverse('conversation-detail', args=[self.conversation.id])

    def test_list_conversations_authenticated(self):
        """Test listing conversations for authenticated user"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.conversation_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Conversation')

    def test_list_conversations_unauthenticated(self):
        """Test listing conversations for unauthenticated user"""
        response = self.client.get(self.conversation_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_conversation(self):
        """Test creating a new conversation"""
        self.client.force_authenticate(user=self.user1)
        data = {
            'title': 'New Conversation',
            'participants': [self.user2.id, self.user3.id]
        }
        response = self.client.post(self.conversation_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)
        
        new_conversation = Conversation.objects.get(title='New Conversation')
        self.assertEqual(new_conversation.owner, self.user1)
        self.assertIn(self.user2, new_conversation.participants.all())
        self.assertIn(self.user3, new_conversation.participants.all())

    def test_retrieve_conversation_as_participant(self):
        """Test retrieving conversation as a participant"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.conversation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Conversation')

    def test_retrieve_conversation_as_non_participant(self):
        """Test retrieving conversation as a non-participant"""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.conversation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_conversation_as_owner(self):
        """Test updating conversation as owner"""
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Updated Conversation Title'}
        response = self.client.patch(self.conversation_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.title, 'Updated Conversation Title')

    def test_update_conversation_as_participant(self):
        """Test updating conversation as participant (not owner)"""
        self.client.force_authenticate(user=self.user2)
        data = {'title': 'Updated Conversation Title'}
        response = self.client.patch(self.conversation_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_conversation_as_owner(self):
        """Test deleting conversation as owner"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.conversation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Conversation.objects.count(), 0)

class MessageAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPass123!'
        )
        self.user3 = User.objects.create_user(
            email='user3@example.com',
            password='TestPass123!'
        )
        
        self.conversation = Conversation.objects.create(
            owner=self.user1,
            title='Test Conversation'
        )
        self.conversation.participants.add(self.user1, self.user2)
        
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Hello, this is a test message!'
        )
        
        self.message_list_url = reverse('message-list')
        self.message_detail_url = reverse('message-detail', args=[self.message.id])

    def test_list_messages_authenticated(self):
        """Test listing messages for authenticated user"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.message_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], 'Hello, this is a test message!')

    def test_list_messages_unauthenticated(self):
        """Test listing messages for unauthenticated user"""
        response = self.client.get(self.message_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_message_as_participant(self):
        """Test creating a message as conversation participant"""
        self.client.force_authenticate(user=self.user2)
        data = {
            'conversation': self.conversation.id,
            'content': 'This is a reply message!'
        }
        response = self.client.post(self.message_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 2)
        
        new_message = Message.objects.get(content='This is a reply message!')
        self.assertEqual(new_message.sender, self.user2)
        self.assertEqual(new_message.conversation, self.conversation)

    def test_create_message_as_non_participant(self):
        """Test creating a message as non-participant"""
        self.client.force_authenticate(user=self.user3)
        data = {
            'conversation': self.conversation.id,
            'content': 'This should not be allowed!'
        }
        response = self.client.post(self.message_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_message_as_participant(self):
        """Test retrieving message as conversation participant"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.message_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Hello, this is a test message!')

    def test_retrieve_message_as_non_participant(self):
        """Test retrieving message as non-participant"""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.message_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_message_as_sender(self):
        """Test updating message as sender"""
        self.client.force_authenticate(user=self.user1)
        data = {'content': 'Updated message content!'}
        response = self.client.patch(self.message_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.message.refresh_from_db()
        self.assertEqual(self.message.content, 'Updated message content!')

    def test_update_message_as_non_sender(self):
        """Test updating message as non-sender"""
        self.client.force_authenticate(user=self.user2)
        data = {'content': 'This should not be allowed!'}
        response = self.client.patch(self.message_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_message_as_read(self):
        """Test marking message as read"""
        self.client.force_authenticate(user=self.user2)
        data = {'is_read': True}
        response = self.client.patch(self.message_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

    def test_delete_message_as_sender(self):
        """Test deleting message as sender"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.message_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Message.objects.count(), 0)

class MessagingPermissionsTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPass123!'
        )
        self.user3 = User.objects.create_user(
            email='user3@example.com',
            password='TestPass123!'
        )
        
        self.conversation = Conversation.objects.create(
            owner=self.user1,
            title='Test Conversation'
        )
        self.conversation.participants.add(self.user1, self.user2)

    def test_participant_permission_conversation(self):
        """Test IsParticipant permission for conversations"""
        # Participant should have access
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('conversation-detail', args=[self.conversation.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Non-participant should not have access
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(reverse('conversation-detail', args=[self.conversation.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_permission_message(self):
        """Test IsParticipant permission for messages"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Test message'
        )
        
        # Participant should have access
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('message-detail', args=[message.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Non-participant should not have access
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(reverse('message-detail', args=[message.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class MessagingSerializerTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='TestPass123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='TestPass123!'
        )
        
        self.conversation = Conversation.objects.create(
            owner=self.user1,
            title='Test Conversation'
        )
        self.conversation.participants.add(self.user1, self.user2)

    def test_conversation_serializer(self):
        """Test conversation serializer"""
        serializer = ConversationSerializer(self.conversation)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Conversation')
        self.assertEqual(data['owner'], self.user1.id)
        self.assertEqual(len(data['participants']), 2)

    def test_message_serializer(self):
        """Test message serializer"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender=self.user1,
            content='Test message'
        )
        
        serializer = MessageSerializer(message)
        data = serializer.data
        
        self.assertEqual(data['content'], 'Test message')
        self.assertEqual(data['sender'], self.user1.id)
        self.assertEqual(data['conversation'], self.conversation.id)
        self.assertFalse(data['is_read'])
