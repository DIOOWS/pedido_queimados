from django.contrib import admin
from .models import (
    Product,
    Order,
    OrderItem,
    Location,
    UserProfile,
    OrderStatusHistory,
)


# =========================================================
# LOCATION
# =========================================================
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# =========================================================
# USER PROFILE
# =========================================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location")
    search_fields = ("user__username", "location__name")
    list_filter = ("location",)


# =========================================================
# PRODUCT
# =========================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# =========================================================
# ORDER ITEM (INLINE)
# =========================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# =========================================================
# ORDER
# =========================================================
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

    list_filter = (
        "status",
        "origin_location",
        "destination_location",
        "created_at",
    )

    search_fields = (
        "id",
        "created_by__username",
        "origin_location__name",
        "destination_location__name",
    )

    ordering = ("-created_at",)
    inlines = [OrderItemInline]


# =========================================================
# ORDER STATUS HISTORY
# =========================================================
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "changed_by", "changed_at")
    list_filter = ("status", "changed_at")
    search_fields = ("order__id", "changed_by__username")
