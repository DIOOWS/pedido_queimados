from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # ====================
    # LOGIN / LOGOUT
    # ====================
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ====================
    # QUEIMADOS (CATÁLOGO)
    # ====================
    path("", views.requisition_list, name="requisition_list"),
    path("requisition/<int:id>/", views.requisition_detail, name="requisition_detail"),
    path("meus-pedidos/", views.user_orders, name="user_orders"),

    # ====================
    # CARRINHO
    # ====================
    path("lista/", views.cart_view, name="cart_view"),
    path("lista/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("lista/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("lista/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("lista/enviar/", views.cart_submit, name="cart_submit"),

    # ====================
    # AUSTIN (ADMIN XODÓ)
    # ====================
    path("xodo-admin/", views.admin_home, name="admin_home"),
    path("xodo-admin/pedidos/", views.order_list, name="order_list"),
    path("xodo-admin/dashboard/", views.dashboard, name="dashboard"),
    path("xodo-admin/pedidos/<int:id>/concluir/", views.conclude_order, name="conclude_order"),

    # ====================
    # DJANGO ADMIN
    # ====================
    path("admin/", admin.site.urls),
]
