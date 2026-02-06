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


# =========================
# LOCATION
# =========================
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


# =========================
# USER PROFILE
# =========================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location")
    list_filter = ("location",)


# =========================
# REQUISITION (CATEGORIAS)
# =========================
@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# =========================
# PRODUCT
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "requisition")
    list_filter = ("requisition",)
    search_fields = ("name",)


# =========================
# ORDER ITEM (INLINE)
# =========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# =========================
# ORDER
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "origin_location",
        "destination_location",
        "status",
        "created_at",
    )
    list_filter = ("status", "origin_location", "destination_location")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]


# =========================
# ORDER STATUS HISTORY
# =========================
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "changed_by", "changed_at")
    list_filter = ("status",)
