from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from pyexpat.errors import messages
from streamlit import login

from .models import Requisition, Product, Order, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def requisition_list(request):
    requisitions = Requisition.objects.all()
    return render(request, "user/requisition_list.html", {"requisitions": requisitions})


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

    return redirect("requisition_list")

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "user/user_orders.html", {"orders": orders})




