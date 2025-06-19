import uuid
from django.db import models

class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    icon = models.ImageField(upload_to='service-icons/', null=True, blank=True)
    image = models.ImageField(upload_to='service-images/', null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='services', blank=True)
    jobs = models.ManyToManyField('jobs.Job', related_name='services', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
