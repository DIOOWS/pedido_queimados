from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import Order, OrderStatusHistory


# =========================================================
# LISTA DE PEDIDOS RECEBIDOS (AUSTIN)
# =========================================================
@staff_member_required
def order_list(request):
    # Garante que o staff é da filial Austin
    if request.user.profile.location.name != "Austin":
        return HttpResponseForbidden("Acesso restrito à filial Austin.")

    orders = Order.objects.filter(
        destination_location__name="Austin"
    ).exclude(
        status=Order.Status.RECEBIDO_ORIGEM
    ).order_by("created_at")

    return render(request, "admin/orders.html", {
        "orders": orders
    })


# =========================================================
# MARCAR PEDIDO COMO ENVIADO (CONCLUIR)
# =========================================================
@staff_member_required
def conclude_order(request, id):
    if request.user.profile.location.name != "Austin":
        return HttpResponseForbidden("Acesso restrito à filial Austin.")

    order = get_object_or_404(
        Order,
        id=id,
        destination_location__name="Austin"
    )

    order.status = Order.Status.ENVIADO
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=Order.Status.ENVIADO,
        changed_by=request.user
    )

    messages.success(
        request,
        f"Pedido #{order.id} marcado como ENVIADO."
    )

    return redirect("order_list")


# =========================================================
# GERAR PDF DO PEDIDO (MANTIDO)
# =========================================================
@staff_member_required
def generate_pdf(request, id):
    if request.user.profile.location.name != "Austin":
        return HttpResponseForbidden("Acesso restrito à filial Austin.")

    order = get_object_or_404(
        Order,
        id=id,
        destination_location__name="Austin"
    )

    html_string = render_to_string("pdf/order.html", {"order": order})
    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f"filename=pedido_{order.id}.pdf"
    return response
