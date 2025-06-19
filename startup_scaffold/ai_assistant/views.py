from rest_framework import viewsets
from .models import AIQuery
from .serializers import AIQuerySerializer
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import openai

class AIQueryViewSet(viewsets.ModelViewSet):
    queryset = AIQuery.objects.all()
    serializer_class = AIQuerySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        query = serializer.validated_data['query_text']
        user = self.request.user
        use_case = serializer.validated_data.get('use_case', '')

        # Call OpenAI API
        openai.api_key = settings.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        ai_response = response['choices'][0]['message']['content']

        # Save with generated response
        serializer.save(user=user, response_text=ai_response, use_case=use_case)
