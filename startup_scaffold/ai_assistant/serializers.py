from rest_framework import serializers
from .models import AIQuery

class AIQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = AIQuery
        fields = ('id', 'user', 'query_text', 'response_text', 'use_case', 'language', 'created_at')
