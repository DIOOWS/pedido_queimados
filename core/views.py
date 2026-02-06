from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Order,
    OrderItem,
    OrderStatusHistory,
    Location,
    Product,
)


def _is_austin(request):
    try:
        return request.user.profile.location.name == "Austin"
    except Exception:
        return False


def _is_queimados(request):
    try:
        return request.user.profile.location.name == "Queimados"
    except Exception:
        return False





def _require_profile_location(request):
    try:
        _ = request.user.profile.location.name
        return None
    except Exception:
        return HttpResponseForbidden("Usuário sem filial configurada. Configure o UserProfile no /admin/.")


# =========================================================
# HOME "/" - SOMENTE QUEIMADOS
# =========================================================
@login_required
def requisition_list(request):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    products = Product.objects.all().order_by("name")
    return render(request, "user/requisition_list.html", {"products": products})


@login_required
def requisition_detail(request, id):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    product = get_object_or_404(Product, id=id)
    return render(request, "user/requisition_detail.html", {"product": product})


# =========================================================
# MEUS PEDIDOS (QUEIMADOS)
# =========================================================
@login_required
def user_orders(request):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    orders = Order.objects.filter(
        origin_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "user/user_orders.html", {"orders": orders})


# =========================================================
# CONFIRMAR RECEBIMENTO (QUEIMADOS)
# =========================================================
@login_required
def confirmar_recebimento(request, order_id):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    order = get_object_or_404(
        Order,
        id=order_id,
        origin_location=request.user.profile.location
    )

    if order.status != Order.Status.ENVIADO:
        messages.error(request, "Este pedido ainda não foi enviado.")
        return redirect("user_orders")

    order.status = Order.Status.RECEBIDO_ORIGEM
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=Order.Status.RECEBIDO_ORIGEM,
        changed_by=request.user
    )

    messages.success(request, f"Pedido #{order.id} confirmado como recebido.")
    return redirect("user_orders")


# =========================================================
# AUSTIN - PAINEL INTERNO
# =========================================================
@login_required
def admin_home(request):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito ao painel interno.")

    return render(request, "admin/home.html")


@login_required
def order_list(request):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito ao painel interno.")

    orders = Order.objects.filter(
        destination_location__name="Austin"
    ).exclude(
        status=Order.Status.RECEBIDO_ORIGEM
    ).order_by("created_at")

    return render(request, "admin/orders.html", {"orders": orders})


@login_required
def update_order_status(request, order_id, new_status):
    err = _require_profile_location(request)
    if err:
        return err

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

    messages.success(request, f"Pedido #{order.id} atualizado para {order.get_status_display()}.")
    return redirect("order_list")


# =========================================================
# CARRINHO (LISTA DE ENVIO) — RECRIADO DO ZERO
# =========================================================

@login_required
def cart_view(request):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    cart = request.session.get("cart", {})
    items = []

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            items.append({
                "product": product,
                "quantity": qty
            })
        except Product.DoesNotExist:
            pass

    return render(request, "user/cart.html", {"items": items})


@login_required
def cart_add(request, product_id):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    request.session["cart"] = cart

    messages.success(request, "Item adicionado à lista.")
    return redirect("cart_view")


@login_required
def cart_update(request, product_id):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    try:
        quantity = int(request.POST.get("quantity", 0))
    except ValueError:
        quantity = 0

    cart = request.session.get("cart", {})

    if quantity > 0:
        cart[str(product_id)] = quantity
    else:
        cart.pop(str(product_id), None)

    request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def cart_remove(request, product_id):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart

    return redirect("cart_view")


@login_required
def cart_submit(request):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito à filial Queimados.")

    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "A lista está vazia.")
        return redirect("cart_view")

    try:
        destino = Location.objects.get(name="Austin")
    except Location.DoesNotExist:
        messages.error(request, "Filial Austin não encontrada.")
        return redirect("cart_view")

    order = Order.objects.create(
        created_by=request.user,
        origin_location=request.user.profile.location,
        destination_location=destino,
        status=Order.Status.CRIADO
    )

    OrderStatusHistory.objects.create(
        order=order,
        status=Order.Status.CRIADO,
        changed_by=request.user
    )

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty
            )
        except Product.DoesNotExist:
            pass

    request.session["cart"] = {}
    messages.success(request, f"Pedido #{order.id} enviado para Austin.")
    return redirect("user_orders")


from django.contrib.auth import authenticate, login, logout


# =========================================================
# LOGIN
# =========================================================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("requisition_list")
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "login.html")


# =========================================================
# LOGOUT
# =========================================================
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")
