from django.shortcuts import render, get_object_or_404
from .models import Order
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

@staff_member_required
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin/orders.html", {"orders": orders})


@staff_member_required
def generate_pdf(request, id):
    order = get_object_or_404(Order, id=id)
    html_string = render_to_string("pdf/order.html", {"order": order})
    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response['Content-Disposition'] = f'filename=pedido_{order.id}.pdf'
    return response
