from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from requisicoes.models import UserProfile, Location

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # tenta colocar um padrão (ex: Queimados)
        default_location = Location.objects.first()
        if default_location:
            UserProfile.objects.create(user=instance, location=default_location)
