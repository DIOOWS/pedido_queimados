from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout

from .models import (
    Order,
    OrderItem,
    OrderStatusHistory,
    Location,
    Product,
    Requisition,
)


# ======================================================
# HELPERS
# ======================================================
def _get_location_name(request):
    """
    Retorna o nome da filial do usuário ou None.
    Evita erro 500 quando não existe profile/location.
    """
    try:
        return request.user.profile.location.name
    except Exception:
        return None


def _require_location(request):
    """
    Se o usuário não tem filial, bloqueia com msg clara.
    """
    loc = _get_location_name(request)
    if not loc:
        return HttpResponseForbidden("Usuário sem filial configurada. Configure o UserProfile no /admin/.")
    return None


def _is_queimados(request):
    return _get_location_name(request) == "Queimados"


def _is_austin(request):
    return _get_location_name(request) == "Austin"


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
            # Austin vai direto pro painel interno
            try:
                if user.profile.location.name == "Austin":
                    return redirect("admin_home")
            except Exception:
                pass
            # Queimados vai pra home (requisition_list)
            return redirect("requisition_list")

        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ======================================================
# HOME "/" (se você quiser usar)
# ======================================================
@login_required
def home(request):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")
    return redirect("requisition_list")


# ======================================================
# QUEIMADOS — REQUISIÇÕES (como era antes)
# ======================================================
@login_required
def requisition_list(request):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    requisitions = Requisition.objects.all().order_by("name")
    return render(request, "user/requisition_list.html", {"requisitions": requisitions})


@login_required
def requisition_detail(request, id):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    requisition = get_object_or_404(Requisition, id=id)
    products = requisition.products.all().order_by("name")

    return render(request, "user/requisition_detail.html", {
        "requisition": requisition,
        "products": products
    })


# ======================================================
# CARRINHO (QUEIMADOS)
# ======================================================
@login_required
def cart_view(request):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    cart = request.session.get("cart", {})
    items = []

    for pid_str, qty in cart.items():
        try:
            product = Product.objects.get(id=int(pid_str))
            items.append({"product": product, "quantity": int(qty)})
        except (Product.DoesNotExist, ValueError, TypeError):
            continue

    return render(request, "user/cart.html", {"items": items})


@login_required
def cart_add(request, product_id):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    try:
        qty = int(request.POST.get("quantity", 0))
    except ValueError:
        qty = 0

    if qty <= 0:
        return redirect("cart_view")

    cart = request.session.get("cart", {})
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + qty
    request.session["cart"] = cart

    return redirect("cart_view")


@login_required
def cart_update(request, product_id):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    cart = request.session.get("cart", {})
    try:
        qty = int(request.POST.get("quantity", 0))
    except ValueError:
        qty = 0

    key = str(product_id)

    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty

    request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def cart_remove(request, product_id):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("cart_view")


@login_required
def cart_submit(request):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Carrinho vazio.")
        return redirect("cart_view")

    try:
        destino = Location.objects.get(name="Austin")
    except Location.DoesNotExist:
        messages.error(request, "Filial destino (Austin) não existe. Crie no /admin/ > Location.")
        return redirect("cart_view")

    # cria pedido
    order = Order.objects.create(
        created_by=request.user,
        origin_location=request.user.profile.location,
        destination_location=destino,
        status=Order.Status.CRIADO,
    )

    # histórico inicial
    OrderStatusHistory.objects.create(
        order=order,
        status=order.status,
        changed_by=request.user
    )

    # itens
    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            q = int(qty)
        except (ValueError, TypeError):
            continue

        if q <= 0:
            continue

        OrderItem.objects.create(
            order=order,
            product_id=pid,
            quantity=q
        )

    request.session["cart"] = {}
    return redirect("order_sent")


@login_required
def order_sent(request):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    return render(request, "user/order_sent.html")


@login_required
def user_orders(request):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    orders = Order.objects.filter(
        origin_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "user/user_orders.html", {"orders": orders})


# ======================================================
# QUEIMADOS — CONFIRMAR RECEBIMENTO (quando Austin enviou)
# ======================================================
@login_required
def confirmar_recebimento(request, id):
    err = _require_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    order = get_object_or_404(
        Order,
        id=id,
        origin_location=request.user.profile.location
    )

    if order.status != Order.Status.ENVIADO:
        messages.error(request, "Este pedido ainda não foi marcado como ENVIADO pela filial destino.")
        return redirect("user_orders")

    order.status = Order.Status.RECEBIDO_ORIGEM
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=order.status,
        changed_by=request.user
    )

    messages.success(request, f"Pedido #{order.id} confirmado como recebido em Queimados.")
    return redirect("user_orders")


# ======================================================
# AUSTIN — ADMIN XODÓ (painel interno)
# ======================================================
@login_required
def admin_home(request):
    err = _require_location(request)
    if err:
        return err

    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito.")

    orders = Order.objects.filter(
        destination_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "admin/orders.html", {"orders": orders})


@login_required
def advance_status(request, id):
    err = _require_location(request)
    if err:
        return err

    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito.")

    order = get_object_or_404(
        Order,
        id=id,
        destination_location=request.user.profile.location
    )

    # Fluxo: CRIADO -> RECEBIDO_DESTINO -> SEPARANDO -> ENVIADO
    if order.status == Order.Status.CRIADO:
        order.status = Order.Status.RECEBIDO_DESTINO
    elif order.status == Order.Status.RECEBIDO_DESTINO:
        order.status = Order.Status.SEPARANDO
    elif order.status == Order.Status.SEPARANDO:
        order.status = Order.Status.ENVIADO
    else:
        # já finalizado ou estado não previsto
        return redirect("admin_home")

    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=order.status,
        changed_by=request.user
    )

    return redirect("admin_home")
