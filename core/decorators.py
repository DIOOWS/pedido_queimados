from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def location_required(location_name: str):
    """
    Restringe uma view para usuários cujo profile.location.name seja igual ao location_name.
    Ex:
        @location_required("Austin")
        def minha_view(...):
            ...
    """
    def decorator(view_func):
        @login_required
        def _wrapped(request, *args, **kwargs):
            prof = getattr(request.user, "profile", None)

            if not prof or not prof.location:
                messages.error(request, "Seu usuário não possui setor definido. Fale com o administrador.")
                return redirect("requisition_list")

            if prof.location.name.strip().lower() != location_name.strip().lower():
                messages.error(request, "Acesso não permitido para seu setor.")
                return redirect("requisition_list")

            return view_func(request, *args, **kwargs)

        return _wrapped
    return decorator
