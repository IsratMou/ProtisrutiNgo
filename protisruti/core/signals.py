from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, SurvivorProfile, CounselorProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create a user profile automatically after user creation
    if it doesn't already exist.
    """
    if created:
        if instance.user_type == 'survivor' and not hasattr(instance, 'survivor_profile'):
            SurvivorProfile.objects.create(user=instance)
        elif instance.user_type == 'counselor' and not hasattr(instance, 'counselor_profile'):
            CounselorProfile.objects.create(user=instance)