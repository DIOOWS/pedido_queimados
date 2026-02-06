from django.apps import AppConfig


class RequisicoesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "requisicoes"

    def ready(self):
        """
        Corrige usuários sem UserProfile ou sem Location
        Executa automaticamente no boot do Django
        """
        try:
            from django.contrib.auth.models import User
            from requisicoes.models import UserProfile, Location

            # tenta pegar Queimados
            queimados = Location.objects.filter(name="Queimados").first()
            if not queimados:
                return

            for user in User.objects.all():
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={"location": queimados},
                )
                if profile.location is None:
                    profile.location = queimados
                    profile.save()

        except Exception:
            # NUNCA quebra o boot por causa disso
            pass
