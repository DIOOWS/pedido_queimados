from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .models import (
    Requisition,
    Product,
    Order,
    OrderItem,
    OrderStatusHistory,
    Location,
)


# =========================================================
# HELPERS (FILIAL / ACESSO)
# =========================================================
def _user_location_name(request) -> str:
    try:
        return (request.user.profile.location.name or "").strip()
    except Exception:
        return ""


def _require_profile_location(request):
    loc = _user_location_name(request)
    if not loc:
        return HttpResponseForbidden("Usuário sem filial configurada. Configure o UserProfile no /admin/.")
    return None


def _is_queimados(request) -> bool:
    return _user_location_name(request).lower() == "queimados"


def _is_austin(request) -> bool:
    return _user_location_name(request).lower() == "austin"


def _can_access_admin_xodo(request) -> bool:
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
# LOGIN / LOGOUT
# =========================================================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Usuário ou senha inválidos.")
            return redirect("login")

        login(request, user)

        # redireciona conforme filial
        loc = ""
        try:
            loc = _user_location_name(request).lower()
        except Exception:
            loc = ""

        if loc == "austin":
            return redirect("admin_home")
        return redirect("requisition_list")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================================================
# HOME "/" — QUEIMADOS (REQUISIÇÕES / CATEGORIAS)
# Austin é redirecionado para o Admin Xodó
# =========================================================
@login_required
def requisition_list(request):
    err = _require_profile_location(request)
    if err:
        return err

    # Austin nunca vê requisições
    if _is_austin(request):
        return redirect("admin_home")

    # só Queimados acessa
    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    requisitions = Requisition.objects.all().order_by("name")

    return render(request, "user/requisition_list.html", {
        "requisitions": requisitions
    })


# =========================================================
# DETALHE DA REQUISIÇÃO — PRODUTOS
# URL: /requisition/<id>/
# =========================================================
@login_required
def requisition_detail(request, id):
    err = _require_profile_location(request)
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


# =========================================================
# CARRINHO (SESSION)
# =========================================================
def _get_cart(request) -> dict:
    return request.session.get("cart", {})


def _save_cart(request, cart: dict):
    request.session["cart"] = cart
    request.session.modified = True


@login_required
def cart_view(request):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    cart = _get_cart(request)  # { "product_id": qty }
    product_ids = [int(pid) for pid in cart.keys()] if cart else []
    products = Product.objects.filter(id__in=product_ids).select_related("requisition")

    items = []
    for p in products:
        qty = int(cart.get(str(p.id), 0))
        if qty > 0:
            items.append({"product": p, "quantity": qty})

    # ordena por requisition e nome
    items.sort(key=lambda x: (x["product"].requisition.name, x["product"].name))

    return render(request, "user/cart.html", {"items": items})


@login_required
def cart_add(request, product_id):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    # garante que o produto existe
    product = get_object_or_404(Product, id=product_id)

    cart = _get_cart(request)
    pid = str(product.id)
    cart[pid] = int(cart.get(pid, 0)) + 1
    _save_cart(request, cart)

    messages.success(request, f"Adicionado: {product.name}")
    return redirect("cart_view")


@login_required
def cart_update(request, product_id):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    if request.method != "POST":
        return HttpResponseForbidden("Método inválido.")

    cart = _get_cart(request)
    pid = str(product_id)

    qty_raw = request.POST.get("quantity", "0")
    try:
        qty = int(qty_raw)
    except ValueError:
        qty = 0

    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty

    _save_cart(request, cart)
    return redirect("cart_view")


@login_required
def cart_remove(request, product_id):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    if request.method != "POST":
        return HttpResponseForbidden("Método inválido.")

    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)
    return redirect("cart_view")


@login_required
def cart_add_bulk(request, requisition_id):
    """
    Adiciona todos os produtos da requisição ao carrinho (qty +1).
    """
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    requisition = get_object_or_404(Requisition, id=requisition_id)
    products = requisition.products.all()

    cart = _get_cart(request)
    for p in products:
        pid = str(p.id)
        cart[pid] = int(cart.get(pid, 0)) + 1

    _save_cart(request, cart)
    messages.success(request, f"Itens adicionados da requisição: {requisition.name}")
    return redirect("cart_view")


@login_required
def cart_submit(request):
    """
    Envia o pedido: cria Order (Queimados -> Austin) com itens do carrinho.
    """
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    if not _is_queimados(request):
        return HttpResponseForbidden("Acesso restrito.")

    if request.method != "POST":
        return HttpResponseForbidden("Método inválido.")

    cart = _get_cart(request)
    if not cart:
        messages.error(request, "Carrinho vazio.")
        return redirect("cart_view")

    # destino Austin (obrigatório existir no banco)
    try:
        destino = Location.objects.get(name__iexact="Austin")
    except Location.DoesNotExist:
        messages.error(request, "Filial de destino (Austin) não encontrada no banco. Crie no /admin/.")
        return redirect("cart_view")

    # cria pedido
    order = Order.objects.create(
        created_by=request.user,
        origin_location=request.user.profile.location,
        destination_location=destino,
        status=Order.Status.CRIADO
    )
    _add_history(order, Order.Status.CRIADO, request.user)

    # cria itens
    product_ids = []
    for pid, qty in cart.items():
        try:
            q = int(qty)
        except ValueError:
            q = 0
        if q > 0:
            product_ids.append(int(pid))

    products = Product.objects.filter(id__in=product_ids)
    prod_map = {p.id: p for p in products}

    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            q = int(qty)
        except ValueError:
            continue
        if q <= 0:
            continue
        if pid not in prod_map:
            continue

        OrderItem.objects.create(
            order=order,
            product=prod_map[pid],
            quantity=q
        )

    # limpa carrinho
    _save_cart(request, {})
    messages.success(request, f"Pedido #{order.id} enviado para Austin!")
    return redirect("order_sent")


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
        return HttpResponseForbidden("Acesso restrito.")

    orders = Order.objects.filter(
        origin_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "user/user_orders.html", {"orders": orders})


@login_required
def order_sent(request):
    return render(request, "user/order_sent.html")


# =========================================================
# ADMIN XODÓ (AUSTIN)
# =========================================================
@login_required
def admin_login_view(request):
    # mantém compatibilidade com sua rota /xodo-admin/login/
    return redirect("login")


@login_required
def admin_home(request):
    err = _require_admin_xodo(request)
    if err:
        return err

    return render(request, "admin/admin_home.html")


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


@login_required
def conclude_order(request, id):
    """
    Botão para Austin avançar status:
    CRIADO -> RECEBIDO -> SEPARANDO -> ENVIADO
    """
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


@login_required
def generate_pdf(request, id):
    err = _require_admin_xodo(request)
    if err:
        return err
    return HttpResponseForbidden("PDF ainda não configurado neste fluxo.")


# =========================================================
# TESTE PDF (opcional)
# =========================================================
@login_required
def test_pdf(request):
    return HttpResponseForbidden("Teste PDF desativado.")
