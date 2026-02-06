from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Requisition, Product


@login_required
def requisition_list(request):
    if request.user.profile.location.name != "Queimados":
        return redirect("admin_home")

    requisitions = Requisition.objects.all()
    return render(request, "user/requisition_list.html", {
        "requisitions": requisitions
    })


@login_required
def requisition_detail(request, id):
    if request.user.profile.location.name != "Queimados":
        return redirect("admin_home")

    requisition = get_object_or_404(Requisition, id=id)
    products = requisition.products.all()

    return render(request, "user/requisition_detail.html", {
        "requisition": requisition,
        "products": products
    })
