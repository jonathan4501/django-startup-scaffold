from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_related_objects(sender, instance, created, **kwargs):
    if created:
        # Placeholder for creating related objects like analytics profile, activity logs, etc.
        # For example:
        # AnalyticsProfile.objects.create(user=instance)
        # ActivityLog.objects.create(user=instance)
        pass
