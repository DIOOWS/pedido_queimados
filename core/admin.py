from django.contrib import admin
from django.utils.html import format_html
from .models import Requisition, Product, Order, OrderItem


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ("name", "image_preview", "icon_preview", "created_at")
    readonly_fields = ("image_preview", "icon_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px; border-radius: 6px;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = "Imagem"

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 6px;" />',
                obj.icon.url
            )
        return "—"

    icon_preview.short_description = "Ícone"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "requisition", "image_preview", "unit")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 120px; border-radius: 6px;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = "Imagem"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "requisition", "created_at", "is_read")
    list_filter = ("is_read", "created_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")
