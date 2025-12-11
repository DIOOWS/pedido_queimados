from django.contrib.auth.decorators import user_passes_test

def receiver_required(view_func):
    """
    Permite acesso somente a:
    - Usuário com permissão can_receive_orders
    - Administrador (is_staff)
    """
    return user_passes_test(
        lambda u: u.is_authenticated and (u.has_perm("core.can_receive_orders") or u.is_staff)
    )(view_func)
