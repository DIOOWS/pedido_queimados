from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Requisition,
    Product,
    Order,
    OrderItem,
    OrderStatusHistory,
    Location
)


def _is_austin(request):
    return request.user.profile.location.name.lower() == "austin"


def _is_queimados(request):
    return request.user.profile.location.name.lower() == "queimados"


def _require_profile_location(request):
    try:
        _ = request.user.profile.location
        return None
    except Exception:
        return HttpResponseForbidden("Usuário sem filial configurada.")


# ===============================
# HOME — REQUISIÇÕES (QUEIMADOS)
# ===============================
@login_required
def requisition_list(request):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    requisitions = Requisition.objects.all().order_by("name")
    return render(request, "user/requisition_list.html", {
        "requisitions": requisitions
    })


# ===============================
# PRODUTOS DA REQUISIÇÃO
# ===============================
@login_required
def requisition_detail(request, id):
    err = _require_profile_location(request)
    if err:
        return err

    if _is_austin(request):
        return redirect("admin_home")

    requisition = get_object_or_404(Requisition, id=id)
    products = requisition.products.all()

    return render(request, "user/requisition_detail.html", {
        "requisition": requisition,
        "products": products
    })


# ===============================
# ADMIN XODÓ — AUSTIN
# ===============================
@login_required
def admin_home(request):
    err = _require_profile_location(request)
    if err:
        return err

    if not _is_austin(request):
        return HttpResponseForbidden("Acesso restrito.")

    orders = Order.objects.filter(
        destination_location=request.user.profile.location
    ).order_by("-created_at")

    return render(request, "admin/admin_home.html", {
        "orders": orders
    })
