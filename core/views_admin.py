from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Order, OrderStatusHistory


# =========================================================
# HELPERS
# =========================================================
def _user_location_name(request):
    try:
        return (request.user.profile.location.name or "").strip()
    except Exception:
        return ""


def _require_profile_location(request):
    loc = _user_location_name(request)
    if not loc:
        return HttpResponseForbidden("Usuário sem filial configurada. Configure o UserProfile no /admin/.")
    return None


def _is_austin(request):
    return _user_location_name(request).lower() == "austin"


def _can_access_admin_xodo(request):
    # Austin acessa /xodo-admin/ mesmo sem staff
    # Superuser também pode (manutenção)
    if request.user.is_superuser:
        return True
    return _is_austin(request)


def _require_admin_xodo(request):
    err = _require_profile_location(request)
    if err:
        return err
    if not _can_access_admin_xodo(request):
        return HttpResponseForbidden("Acesso restrito ao painel interno (Austin).")
    return None


def _add_history(order, status, user):
    OrderStatusHistory.objects.create(
        order=order,
        status=status,
        changed_by=user
    )


# =========================================================
# HOME DO ADMIN XODÓ (AUSTIN)
# usa a tela do painel interno que você já tem
# =========================================================
@login_required
def admin_home(request):
    err = _require_admin_xodo(request)
    if err:
        return err

    # você pode manter um template simples com links (ou o que já existe)
    # caso não exista, crie: templates/admin/admin_home.html
    return render(request, "admin/admin_home.html")


# =========================================================
# LISTA DE PEDIDOS (AUSTIN) - só pedidos destinados a Austin
# =========================================================
@login_required
def order_list(request):
    err = _require_admin_xodo(request)
    if err:
        return err

    austin_location = request.user.profile.location
    orders = Order.objects.filter(
        destination_location=austin_location
    ).order_by("-created_at")

    return render(request, "admin/orders.html", {"orders": orders})


# =========================================================
# DASHBOARD (AUSTIN) - contadores rápidos
# =========================================================
@login_required
def dashboard(request):
    err = _require_admin_xodo(request)
    if err:
        return err

    austin_location = request.user.profile.location

    qs = Order.objects.filter(destination_location=austin_location)
    data = {
        "total": qs.count(),
        "criado": qs.filter(status=Order.Status.CRIADO).count(),
        "recebido": qs.filter(status=Order.Status.RECEBIDO).count(),
        "separando": qs.filter(status=Order.Status.SEPARANDO).count(),
        "enviado": qs.filter(status=Order.Status.ENVIADO).count(),
        "recebido_origem": qs.filter(status=Order.Status.RECEBIDO_ORIGEM).count(),
    }

    return render(request, "admin/dashboard.html", data)


# =========================================================
# AÇÃO ÚNICA: AVANÇAR STATUS (botão "Concluir/Avançar")
# Fluxo:
# CRIADO -> RECEBIDO -> SEPARANDO -> ENVIADO
# =========================================================
@login_required
def conclude_order(request, id):
    err = _require_admin_xodo(request)
    if err:
        return err

    if request.method != "POST":
        return HttpResponseForbidden("Método inválido.")

    austin_location = request.user.profile.location

    order = get_object_or_404(
        Order,
        id=id,
        destination_location=austin_location
    )

    # Avança no fluxo
    if order.status == Order.Status.CRIADO:
        order.status = Order.Status.RECEBIDO
        order.save()
        _add_history(order, Order.Status.RECEBIDO, request.user)
        messages.success(request, f"Pedido #{order.id}: marcado como RECEBIDO.")

    elif order.status == Order.Status.RECEBIDO:
        order.status = Order.Status.SEPARANDO
        order.save()
        _add_history(order, Order.Status.SEPARANDO, request.user)
        messages.success(request, f"Pedido #{order.id}: marcado como SEPARANDO.")

    elif order.status == Order.Status.SEPARANDO:
        order.status = Order.Status.ENVIADO
        order.save()
        _add_history(order, Order.Status.ENVIADO, request.user)
        messages.success(request, f"Pedido #{order.id}: marcado como ENVIADO.")

    else:
        messages.warning(request, f"Pedido #{order.id} já está em status final ({order.get_status_display()}).")

    return redirect("order_list")


# =========================================================
# PDF (opcional) - por enquanto desativado
# =========================================================
@login_required
def generate_pdf(request, id):
    err = _require_admin_xodo(request)
    if err:
        return err

    return HttpResponseForbidden("PDF ainda não configurado neste fluxo.")
