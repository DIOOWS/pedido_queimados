from django.contrib import admin
from .models import Requisition, Product, Order
# ... seus admins RequisitionAdmin e ProductAdmin


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "requisition", "status", "created_at", "concluded_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "requisition__name")
    ordering = ("-created_at",)


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    readonly_fields = ("image_preview", "icon_preview")

    def image_preview(self, obj):
        if obj.image:
            return obj.image.image_tag()
        return "-"

    def icon_preview(self, obj):
        if obj.icon:
            return obj.icon.image_tag()
        return "-"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "requisition")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return obj.image.image_tag()
        return "-"

