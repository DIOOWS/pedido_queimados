from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from django.views.decorators.http import require_POST

from xhtml2pdf import pisa

from .models import Requisition, Product, Order, OrderItem


# ============================================================
# UTIL
# ============================================================

def get_pending_orders():
    return Order.objects.filter(status="PENDENTE").count()


def _get_cart(session):
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    session["cart"] = cart
    return cart


# ============================================================
# LOGIN / LOGOUT – USUÁRIO
# ============================================================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("requisition_list")

        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# ============================================================
# LOGIN ADMIN / SETOR
# ============================================================

def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_home")

        messages.error(request, "Acesso não permitido.")

    return render(request, "admin_login.html")


@user_passes_test(lambda u: u.is_staff)
def admin_home(request):
    return render(request, "admin/home.html", {
        "pending_orders": get_pending_orders()
    })


# ============================================================
# ÁREA DO USUÁRIO – REQUISIÇÕES
# ============================================================

@login_required
def requisition_list(request):
    requisitions = Requisition.objects.all()
    pending_orders = get_pending_orders() if request.user.is_staff else 0

    return render(request, "user/requisition_list.html", {
        "requisitions": requisitions,
        "pending_orders": pending_orders
    })


@login_required
def requisition_detail(request, id):
    requisition = get_object_or_404(Requisition, id=id)
    products = requisition.products.all()

    return render(request, "user/requisition_detail.html", {
        "requisition": requisition,
        "products": products
    })


@login_required
def user_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )
    return render(request, "user/user_orders.html", {"orders": orders})


def order_sent(request):
    return render(request, "user/order_sent.html")


# ============================================================
# CARRINHO (LISTA DE ENVIO) – 1 PEDIDO ÚNICO
# ============================================================

@login_required
@require_POST
def cart_add(request, product_id):
    cart = _get_cart(request.session)
    qty = int(request.POST.get("quantity", "0") or 0)

    if qty > 0:
        key = str(product_id)
        cart[key] = cart.get(key, 0) + qty
        request.session.modified = True

    return redirect(request.META.get("HTTP_REFERER", "cart_view"))


@login_required
def cart_view(request):
    cart = _get_cart(request.session)
    product_ids = [int(pid) for pid in cart.keys()] if cart else []

    products = (
        Product.objects
        .select_related("requisition")
        .filter(id__in=product_ids)
    )

    items = []
    for p in products:
        items.append({
            "product": p,
            "quantity": int(cart.get(str(p.id), 0))
        })

    items.sort(key=lambda x: (x["product"].requisition.name, x["product"].name))

    return render(request, "user/cart.html", {"items": items})


@login_required
@require_POST
def cart_update(request, product_id):
    cart = _get_cart(request.session)
    qty = int(request.POST.get("quantity", "0") or 0)
    key = str(product_id)

    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty

    request.session.modified = True
    return redirect("cart_view")


@login_required
@require_POST
def cart_remove(request, product_id):
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    request.session.modified = True
    return redirect("cart_view")


@login_required
@require_POST
def cart_submit(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.warning(request, "Sua lista está vazia.")
        return redirect("cart_view")

    product_ids = [int(pid) for pid in cart.keys()]
    products = (
        Product.objects
        .select_related("requisition")
        .filter(id__in=product_ids)
    )

    with transaction.atomic():
        order = Order.objects.create(user=request.user, status="PENDENTE")

        for p in products:
            qty = int(cart.get(str(p.id), 0))
            if qty > 0:
                OrderItem.objects.create(order=order, product=p, quantity=qty)

    request.session["cart"] = {}
    request.session.modified = True

    messages.success(request, "Pedido enviado com sucesso ✅")
    return redirect("order_sent")


# ============================================================
# ✅ ADD BULK (ATUALIZADO) – VOLTA PRA MESMA REQUISIÇÃO
# ============================================================

@login_required
@require_POST
def cart_add_bulk(request, requisition_id):
    """
    Recebe vários produtos/quantidades de uma tela de requisição (qty_<id>)
    e soma no carrinho da sessão.
    Depois volta para a mesma tela, mostra mensagem e zera inputs via JS.
    """
    cart = _get_cart(request.session)

    added_any = False

    for key, value in request.POST.items():
        if not key.startswith("qty_"):
            continue

        product_id = key.replace("qty_", "")
        if not product_id.isdigit():
            continue

        try:
            qty = int(value)
        except ValueError:
            qty = 0

        if qty > 0:
            pid = str(int(product_id))
            cart[pid] = cart.get(pid, 0) + qty
            added_any = True

    request.session.modified = True

    if added_any:
        messages.success(request, "Itens adicionados na lista ✅")
    else:
        messages.warning(request, "Nenhum item foi adicionado (tudo 0).")

    return redirect("requisition_detail", id=requisition_id)


# ============================================================
# ÁREA DO SETOR (ESTOQUE)
# ============================================================

@staff_member_required
def order_list(request):
    orders = (
        Order.objects
        .filter(status="PENDENTE")
        .select_related("user")
        .prefetch_related("items__product__requisition")
        .order_by("-created_at")
    )

    return render(request, "admin/orders.html", {
        "orders": orders,
        "pending_orders": orders.count()
    })


@staff_member_required
@require_POST
def conclude_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.status = "CONCLUIDO"
    order.concluded_at = timezone.now()
    order.save()
    return redirect("order_list")


# ============================================================
# PDF (OTIMIZADO / SEM LOGO / SEM QR)
# ============================================================

@staff_member_required
def generate_pdf(request, id):
    order = (
        Order.objects
        .select_related("user")
        .prefetch_related("items__product__requisition")
        .get(id=id)
    )

    template = get_template("pdf/order.html")
    html = template.render({"order": order})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="pedido_{order.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response, encoding="utf-8")
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)

    return response


# ============================================================
# DASHBOARD
# ============================================================

@staff_member_required
def dashboard(request):
    pending_orders = get_pending_orders()

    pedidos_por_dia = (
        Order.objects.values("created_at__date")
        .annotate(total=Count("id"))
        .order_by("created_at__date")
    )

    produtos_mais_pedidos = (
        OrderItem.objects.values("product__name")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:5]
    )

    return render(request, "admin/dashboard.html", {
        "pedidos_por_dia": pedidos_por_dia,
        "produtos_mais_pedidos": produtos_mais_pedidos,
        "pending_orders": pending_orders
    })


# ============================================================
# TESTE PDF (opcional)
# ============================================================

def test_pdf(request):
    html = """
    <h1>PDF TESTE</h1>
    <p>Se você vê isso, o xhtml2pdf está funcionando.</p>
    """
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="teste.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("ERRO ao gerar PDF", status=500)
    return response
