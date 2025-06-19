import uuid
from django.db import models
from django.conf import settings

class AIQuery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    use_case = models.CharField(max_length=100, blank=True)  # e.g., "job_posting", "profile_help"
    language = models.CharField(max_length=10, default="en")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Query by {self.user.email} at {self.created_at}"
