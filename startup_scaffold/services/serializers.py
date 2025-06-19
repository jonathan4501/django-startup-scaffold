from rest_framework import serializers
from core.serializers import TimeStampedSerializer, UUIDSerializer, DynamicFieldsMixin
from jobs.serializers import SkillSerializer, JobSerializer
from .models import Service

class ServiceSerializer(DynamicFieldsMixin, UUIDSerializer, TimeStampedSerializer, serializers.ModelSerializer):
    """
    Comprehensive serializer for Service model with nested relationships.
    Inherits from:
    - DynamicFieldsMixin: Allows dynamic field selection
    - UUIDSerializer: Handles UUID primary key
    - TimeStampedSerializer: Handles created_at and updated_at fields
    """
    skills = SkillSerializer(many=True, read_only=True)
    jobs = JobSerializer(many=True, read_only=True)
    
    # For write operations, we need separate fields for the relationships
    skill_ids = serializers.PrimaryKeyRelatedField(
        source='skills',
        queryset=Service.objects.none(),  # Will be set in __init__
        write_only=True,
        many=True,
        required=False
    )
    
    job_ids = serializers.PrimaryKeyRelatedField(
        source='jobs',
        queryset=Service.objects.none(),  # Will be set in __init__
        write_only=True,
        many=True,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets for relationship fields
        from jobs.models import Skill, Job
        self.fields['skill_ids'].queryset = Skill.objects.all()
        self.fields['job_ids'].queryset = Job.objects.all()

    class Meta:
        model = Service
        fields = (
            'id',
            'name',
            'description',
            'is_active',
            'is_public',
            'icon',
            'image',
            'skills',
            'skill_ids',
            'jobs',
            'job_ids',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_icon(self, value):
        """Validate icon file size and type if needed"""
        if value and value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Icon file too large. Size should not exceed 5MB.")
        return value

    def validate_image(self, value):
        """Validate image file size and type if needed"""
        if value and value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("Image file too large. Size should not exceed 10MB.")
        return value
