from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from requisicoes.models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # ✅ cria profile sem filial (o usuário escolhe no /setup/)
        UserProfile.objects.create(user=instance, location=None)
