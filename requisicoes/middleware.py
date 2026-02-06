from requisicoes.models import UserProfile, Location

class EnsureUserProfileMiddleware:
    """
    Garante que todo usuário autenticado tenha UserProfile e Location
    SEM quebrar o sistema
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
            except Exception:
                location = Location.objects.first()
                if location:
                    UserProfile.objects.create(
                        user=request.user,
                        location=location
                    )

        return self.get_response(request)
