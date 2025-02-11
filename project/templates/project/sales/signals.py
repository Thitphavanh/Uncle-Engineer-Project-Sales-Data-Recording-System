from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *


@receiver(post_save, sender=User)
def create_custom_user(sender, instance, created, **kwargs):
    if created:
        # Create a CustomUser instance when a new User is created
        CustomUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_custom_user(sender, instance, **kwargs):
    # Save the CustomUser instance whenever the User is saved
    if hasattr(instance, "customuser"):
        instance.customuser.save()
