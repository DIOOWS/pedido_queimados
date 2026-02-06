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


def _is_queimados(request):
    return _user_location_name(request).lower() == "queimados"


def _is_austin(request):
    return _user_location_name(request).lower() == "austin"


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
        try:
            loc = _user_location_name(request).lower()
            if loc == "austin":
                return redirect("admin_home")
        except Exception:
            pass
        return redirect("requisition_list")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================================================
# HOME "/" — SOMENTE QUEIMADOS (REQUISIÇÕES / CATEGORIAS)
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
# DETALHE DA REQUISIÇÃO — LISTA PRODUTOS DAQUELA REQUISIÇÃO
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
# (PLACEHOLDERS) — Mantém compatibilidade com seu urls.py
# Se já existe no seu projeto, pode substituir depois
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
    orders = Order.objects.filter(origin_location=request.user.profile.location).order_by("-created_at")
    return render(request, "user/user_orders.html", {"orders": orders})


@login_required
def order_sent(request):
    return render(request, "user/order_sent.html")


# =========================================================
# ADMIN XODÓ (AUSTIN) — placeholders pra não quebrar import
# Você disse que quer usar a tela do painel interno existente.
# Vamos ajustar isso no próximo arquivo (views_admin.py).
# =========================================================

@login_required
def admin_login_view(request):
    # opcional: pode apontar pro login padrão do sistema
    return redirect("login")


@login_required
def admin_home(request):
    # Se Austin -> mostra painel
    err = _require_profile_location(request)
    if err:
        return err
    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito.")

    orders = Order.objects.filter(
        destination_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "admin/admin_home.html", {"orders": orders})


@login_required
def order_list(request):
    return admin_home(request)


@login_required
def dashboard(request):
    return admin_home(request)


@login_required
def generate_pdf(request, id):
    return HttpResponseForbidden("PDF ainda não configurado.")


@login_required
def conclude_order(request, id):
    return HttpResponseForbidden("Ação ainda não configurada.")


# =========================================================
# CARRINHO — placeholders (vamos restaurar no próximo passo)
# =========================================================

@login_required
def cart_view(request):
    return HttpResponseForbidden("Carrinho ainda não configurado.")


@login_required
def cart_add(request, product_id):
    return HttpResponseForbidden("Carrinho ainda não configurado.")


@login_required
def cart_update(request, product_id):
    return HttpResponseForbidden("Carrinho ainda não configurado.")


@login_required
def cart_remove(request, product_id):
    return HttpResponseForbidden("Carrinho ainda não configurado.")


@login_required
def cart_submit(request):
    return HttpResponseForbidden("Carrinho ainda não configurado.")


@login_required
def cart_add_bulk(request, requisition_id):
    return HttpResponseForbidden("Carrinho ainda não configurado.")


@login_required
def test_pdf(request):
    return HttpResponseForbidden("Teste PDF desativado.")
