from django.contrib import admin
from .models import (
    Location,
    UserProfile,
    Requisition,
    Product,
    Order,
    OrderItem
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "location")


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    inlines = [ProductInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "origin_location", "destination_location", "status", "created_at")
    inlines = [OrderItemInline]
