from django.contrib import admin
from .models import Requisition, Product


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
