from django.shortcuts import redirect
from django.urls import reverse
from django.db.utils import ProgrammingError, OperationalError
from django.contrib.auth.models import AnonymousUser

from .models import UserProfile, Location


class EnsureUserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or ""

        # ✅ Não mexe com admin, static e login (evita travar o painel)
        if (
            path.startswith("/admin/")
            or path.startswith("/static/")
            or path.startswith("/login/")
        ):
            return self.get_response(request)

        user = getattr(request, "user", AnonymousUser())

        # Só faz algo se estiver logado
        if not user.is_authenticated:
            return self.get_response(request)

        try:
            # tenta pegar/garantir profile
            profile = getattr(user, "profile", None)

            if profile is None:
                # tenta pegar uma filial padrão
                location = Location.objects.first()
                if location:
                    UserProfile.objects.get_or_create(
                        user=user, defaults={"location": location}
                    )

        except (ProgrammingError, OperationalError):
            # ✅ Tabelas ainda não existem / migrations não rodaram
            # Não derruba o site.
            return self.get_response(request)

        return self.get_response(request)
