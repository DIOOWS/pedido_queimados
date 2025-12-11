from django.contrib import admin
from django.utils.html import format_html

from .models import Requisition, Product, Order, OrderItem

@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_preview")
    fields = ("name", "description", "icon")

    readonly_fields = ("icon_preview",)

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:contain;border-radius:8px;">', obj.icon.url)
        return "(Nenhum ícone)"



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "requisition", "unit", "image")
    list_filter = ("requisition",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "requisition", "created_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")
