from django.db import models
from django.conf import settings

class Review(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='given_reviews',
        on_delete=models.CASCADE
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_reviews',
        on_delete=models.CASCADE
    )
    job = models.ForeignKey(
        'jobs.Job',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    shift = models.ForeignKey(
        'shifts.Shift',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1)  # e.g., 4.5
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reviewer', 'reviewee', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.id} by {self.reviewer} for {self.reviewee}"
