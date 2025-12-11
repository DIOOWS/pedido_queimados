from core.models import Order

def pending_orders(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {"pending_orders": Order.objects.filter(is_read=False).count()}
    return {"pending_orders": 0}
