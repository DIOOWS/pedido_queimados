from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import get_template
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Sum
from django.conf import settings
from django.utils import timezone

import base64
import os
from io import BytesIO

from xhtml2pdf import pisa
import qrcode

from .models import Requisition, Product, Order, OrderItem


# ============================================================
# CONTADOR DE PEDIDOS PENDENTES
# ============================================================

def get_pending_orders():
    return Order.objects.filter(status="PENDENTE").count()


# ============================================================
# LOGIN / LOGOUT – USUÁRIO COMUM
# ============================================================

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
    pending_orders = get_pending_orders()
    return render(request, "admin/home.html", {
        "pending_orders": pending_orders
    })


# ============================================================
# ÁREA DO USUÁRIO – ENVIO DE PEDIDOS
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
def send_order(request, id):
    requisition = get_object_or_404(Requisition, id=id)

    order = Order.objects.create(
        user=request.user,
        requisition=requisition
    )

    for product_id, quantity in request.POST.items():
        if quantity.isdigit() and int(quantity) > 0:
            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                quantity=int(quantity)
            )

    return redirect("order_sent")


@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "user/user_orders.html", {"orders": orders})


def order_sent(request):
    return render(request, "user/order_sent.html")


@login_required
def order_preview(request, id):
    order = get_object_or_404(Order, id=id)

    # Mantém QR aqui se você ainda usa essa tela (não mexi nela)
    scheme = "https" if request.is_secure() else "http"
    qr_url = f"{scheme}://{request.get_host()}/xodo-admin/pedidos/{order.id}"

    qr = qrcode.make(qr_url)
    buffer = BytesIO()
    qr.save(buffer, "PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "user/order_preview.html", {
        "order": order,
        "qr_code": qr_base64,
        "qr_url": qr_url,
    })


# ============================================================
# ÁREA DO SETOR (ESTOQUE)
# ============================================================

@staff_member_required
def order_list(request):
    orders = Order.objects.filter(status="PENDENTE").order_by("-created_at")
    pending_orders = Order.objects.filter(status="PENDENTE").count()

    return render(request, "admin/orders.html", {
        "orders": orders,
        "pending_orders": pending_orders
    })


@staff_member_required
def conclude_order(request, id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=id)
        order.status = "CONCLUIDO"
        order.concluded_at = timezone.now()
        order.save()
    return redirect("order_list")


# ============================================================
# TESTE DE PDF — DIAGNÓSTICO (Render)
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


# ============================================================
# GERAR PDF — SEM QR CODE
# ============================================================

@staff_member_required
def generate_pdf(request, id):
    order = get_object_or_404(Order, id=id)
    template = get_template("pdf/order.html")

    # ==== LOGO ====
    logo_path = os.path.join(settings.BASE_DIR, "core", "static", "logo_xodo.png")
    logo_path = logo_path.replace("\\", "/")
    logo_url = f"file:///{logo_path}"

    html = template.render({
        "order": order,
        "logo_path": logo_url,
    })

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
