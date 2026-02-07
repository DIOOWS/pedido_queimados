from django.db.utils import ProgrammingError, OperationalError
from django.contrib.auth.models import AnonymousUser

from .models import UserProfile, Location


class EnsureUserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or ""

        # ✅ Não mexe com admin, static, login e arquivos comuns
        if (
            path.startswith("/admin/")
            or path.startswith("/static/")
            or path.startswith("/login/")
            or path == "/favicon.ico"
            or path.startswith("/image/")
        ):
            return self.get_response(request)

        user = getattr(request, "user", AnonymousUser())

        if not user.is_authenticated:
            return self.get_response(request)

        try:
            profile = getattr(user, "profile", None)

            if profile is None:
                location = Location.objects.first()
                if location:
                    UserProfile.objects.get_or_create(
                        user=user, defaults={"location": location}
                    )

        except (ProgrammingError, OperationalError):
            return self.get_response(request)

        return self.get_response(request)
