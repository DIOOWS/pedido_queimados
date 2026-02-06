from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Order, OrderStatusHistory


def _is_austin(request):
    try:
        return request.user.profile.location.name == "Austin"
    except Exception:
        return False


# =========================================================
# HOME DO PAINEL INTERNO (AUSTIN)
# URL: /xodo-admin/
# =========================================================
@login_required
def admin_home(request):
    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito ao painel interno.")

    return render(request, "admin/home.html")


# =========================================================
# LISTA DE PEDIDOS RECEBIDOS (AUSTIN)
# URL: /xodo-admin/pedidos/
# =========================================================
@login_required
def order_list(request):
    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito ao painel interno.")

    orders = Order.objects.filter(
        destination_location__name="Austin"
    ).exclude(
        status=Order.Status.RECEBIDO_ORIGEM
    ).order_by("created_at")

    return render(request, "admin/orders.html", {
        "orders": orders
    })


# =========================================================
# ATUALIZAR STATUS DO PEDIDO (AUSTIN)
# =========================================================
@login_required
def update_order_status(request, order_id, new_status):
    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito ao painel interno.")

    order = get_object_or_404(
        Order,
        id=order_id,
        destination_location__name="Austin"
    )

    allowed = [
        Order.Status.RECEBIDO,
        Order.Status.SEPARANDO,
        Order.Status.ENVIADO,
    ]

    if new_status not in allowed:
        messages.error(request, "Status inválido.")
        return redirect("order_list")

    order.status = new_status
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=new_status,
        changed_by=request.user
    )

    messages.success(
        request,
        f"Pedido #{order.id} atualizado para {order.get_status_display()}."
    )

    return redirect("order_list")
