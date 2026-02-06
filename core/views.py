from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout

from .models import (
    Requisition,
    Product,
    Order,
    OrderItem,
    OrderStatusHistory,
    Location,
)

# ======================================================
# HELPERS
# ======================================================
def _location_name(request):
    try:
        return request.user.profile.location.name
    except Exception:
        return None


def _is_queimados(request):
    return _location_name(request) == "Queimados"


def _is_austin(request):
    return _location_name(request) == "Austin"


# ======================================================
# LOGIN / LOGOUT
# ======================================================
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ======================================================
# HOME
# ======================================================
@login_required
def home(request):
    if _is_austin(request):
        return redirect("admin_home")
    return redirect("requisition_list")


# ======================================================
# QUEIMADOS — REQUISIÇÕES
# ======================================================
@login_required
def requisition_list(request):
    if not _is_queimados(request):
        return HttpResponseForbidden()

    requisitions = Requisition.objects.all()
    return render(request, "user/requisition_list.html", {
        "requisitions": requisitions
    })


@login_required
def requisition_detail(request, id):
    if not _is_queimados(request):
        return HttpResponseForbidden()

    requisition = get_object_or_404(Requisition, id=id)
    products = requisition.products.all()

    return render(request, "user/requisition_detail.html", {
        "requisition": requisition,
        "products": products
    })


# ======================================================
# CARRINHO
# ======================================================
@login_required
def cart_view(request):
    if not _is_queimados(request):
        return HttpResponseForbidden()

    cart = request.session.get("cart", {})
    items = []

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        items.append({"product": product, "quantity": qty})

    return render(request, "user/cart.html", {"items": items})


@login_required
def cart_add(request, product_id):
    if not _is_queimados(request):
        return HttpResponseForbidden()

    qty = int(request.POST.get("quantity", 0))
    if qty <= 0:
        return redirect("cart_view")

    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    request.session["cart"] = cart

    return redirect("cart_view")


@login_required
def cart_update(request, product_id):
    cart = request.session.get("cart", {})
    qty = int(request.POST.get("quantity", 0))

    if qty <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = qty

    request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def cart_remove(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def cart_submit(request):
    if not _is_queimados(request):
        return HttpResponseForbidden()

    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Carrinho vazio.")
        return redirect("cart_view")

    destino = Location.objects.get(name="Austin")

    order = Order.objects.create(
        created_by=request.user,
        origin_location=request.user.profile.location,
        destination_location=destino,
    )

    OrderStatusHistory.objects.create(
        order=order,
        status=Order.Status.CRIADO,
        changed_by=request.user
    )

    for pid, qty in cart.items():
        OrderItem.objects.create(
            order=order,
            product_id=pid,
            quantity=qty
        )

    request.session["cart"] = {}
    return redirect("order_sent")


@login_required
def order_sent(request):
    return render(request, "user/order_sent.html")


@login_required
def user_orders(request):
    if not _is_queimados(request):
        return HttpResponseForbidden()

    orders = Order.objects.filter(
        origin_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "user/user_orders.html", {"orders": orders})


# ======================================================
# AUSTIN — ADMIN XODÓ
# ======================================================
@login_required
def admin_home(request):
    if not _is_austin(request):
        return HttpResponseForbidden()

    orders = Order.objects.filter(
        destination_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "admin/orders.html", {"orders": orders})


@login_required
def advance_status(request, id):
    if not _is_austin(request):
        return HttpResponseForbidden()

    order = get_object_or_404(Order, id=id)

    if order.status == Order.Status.CRIADO:
        order.status = Order.Status.SEPARANDO
    elif order.status == Order.Status.SEPARANDO:
        order.status = Order.Status.ENVIADO

    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=order.status,
        changed_by=request.user
    )

    return redirect("admin_home")
