from django.contrib import admin
from .models import (
    Requisition,
    Product,
    Order,
    OrderItem,
    Location,
    UserProfile
)


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "requisition")
    list_filter = ("requisition",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "origin_location", "destination_location", "status", "created_at")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]


admin.site.register(Location)
admin.site.register(UserProfile)
