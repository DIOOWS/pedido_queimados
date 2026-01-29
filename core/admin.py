from django.contrib import admin
from .models import Requisition, Product, Order, Location, UserProfile


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

    # se quiser garantir que apareça no formulário:
    fields = ("name", "description", "image", "image_preview", "icon", "icon_preview")

    @admin.display(description="Preview da imagem")
    def image_preview(self, obj):
        if obj.image:
            return obj.image.image_tag()
        return "-"

    @admin.display(description="Preview do ícone")
    def icon_preview(self, obj):
        if obj.icon:
            return obj.icon.image_tag()
        return "-"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "requisition")
    readonly_fields = ("image_preview",)

    fields = ("requisition", "name", "image", "image_preview", "unit")

    @admin.display(description="Preview da imagem")
    def image_preview(self, obj):
        if obj.image:
            return obj.image.image_tag()
        return "-"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "last_seen")
    list_filter = ("location",)
    search_fields = ("user__username", "user__email", "location__name")
