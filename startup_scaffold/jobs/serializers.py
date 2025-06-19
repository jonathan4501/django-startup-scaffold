from rest_framework import serializers
from .models import Job, Skill, Location, JobApplication, JobRecommendation

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'city', 'state', 'country')

class JobSerializer(serializers.ModelSerializer):
    required_skills = SkillSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Job
        fields = ('id', 'client', 'title', 'description', 'required_skills', 'location', 'budget', 'shift', 'status', 'created_at', 'updated_at')

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ('id', 'job', 'worker', 'applied_at', 'is_hired')

class JobRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRecommendation
        fields = ('id', 'worker', 'job', 'recommended_at')
