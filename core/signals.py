from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from requisicoes.models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Cria o profile automaticamente quando cria usuário.
    NÃO faz query em Location aqui (evita 500 no deploy).
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
