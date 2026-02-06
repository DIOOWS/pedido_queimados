from django.contrib import admin
from .models import (
    Location,
    UserProfile,
    Requisition,
    Product,
    Order,
    OrderItem,
    OrderStatusHistory,
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "location")
    search_fields = ("user__username", "user__email", "location__name")
    list_filter = ("location",)


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "requisition")
    search_fields = ("name", "requisition__name")
    list_filter = ("requisition",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_by",
        "origin_location",
        "destination_location",
        "status",
        "created_at",
    )
    list_filter = ("status", "origin_location", "destination_location", "created_at")
    search_fields = ("id", "created_by__username", "created_by__email")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "status", "changed_by", "changed_at")
    list_filter = ("status", "changed_at")
    search_fields = ("order__id", "changed_by__username")
    ordering = ("-changed_at",)
