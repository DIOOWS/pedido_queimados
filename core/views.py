from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Order,
    OrderItem,
    OrderStatusHistory,
    Location,
    Product
)


# =========================================================
# CRIAR PEDIDO - SOMENTE QUEIMADOS
# =========================================================
@login_required
def criar_pedido(request):
    user_location = request.user.profile.location.name

    if user_location != "Queimados":
        return HttpResponseForbidden("Apenas a filial Queimados pode criar pedidos.")

    if request.method == "POST":
        try:
            destino = Location.objects.get(name="Austin")
        except Location.DoesNotExist:
            messages.error(request, "Filial de destino (Austin) não encontrada.")
            return redirect("criar_pedido")

        # Cria o pedido
        order = Order.objects.create(
            created_by=request.user,
            origin_location=request.user.profile.location,
            destination_location=destino,
            status=Order.Status.CRIADO
        )

        # Histórico inicial
        OrderStatusHistory.objects.create(
            order=order,
            status=Order.Status.CRIADO,
            changed_by=request.user
        )

        produtos = request.POST.getlist("product")
        quantidades = request.POST.getlist("quantity")

        for product_id, quantity in zip(produtos, quantidades):
            if product_id and quantity:
                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=int(quantity)
                )

        messages.success(request, f"Pedido #{order.id} criado com sucesso.")
        return redirect("meus_pedidos")

    produtos = Product.objects.all().order_by("name")

    return render(request, "user/criar_pedido.html", {
        "produtos": produtos
    })


# =========================================================
# LISTA DE PEDIDOS DE QUEIMADOS
# =========================================================
@login_required
def meus_pedidos(request):
    user_location = request.user.profile.location.name

    if user_location != "Queimados":
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    pedidos = Order.objects.filter(
        origin_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "user/meus_pedidos.html", {
        "pedidos": pedidos
    })


# =========================================================
# CONFIRMAR RECEBIMENTO (QUEIMADOS)
# =========================================================
@login_required
def confirmar_recebimento(request, order_id):
    user_location = request.user.profile.location.name

    if user_location != "Queimados":
        return HttpResponseForbidden()

    order = get_object_or_404(
        Order,
        id=order_id,
        origin_location=request.user.profile.location
    )

    if order.status != Order.Status.ENVIADO:
        messages.error(request, "Este pedido ainda não foi enviado.")
        return redirect("meus_pedidos")

    order.status = Order.Status.RECEBIDO_ORIGEM
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=Order.Status.RECEBIDO_ORIGEM,
        changed_by=request.user
    )

    messages.success(request, f"Pedido #{order.id} confirmado como recebido.")
    return redirect("meus_pedidos")
