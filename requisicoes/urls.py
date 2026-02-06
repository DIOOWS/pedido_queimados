from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [

    # ====================
    # LOGIN / LOGOUT
    # ====================
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ====================
    # QUEIMADOS (USUÁRIO)
    # ====================
    path("", views.requisition_list, name="requisition_list"),
    path("requisition/<int:id>/", views.requisition_detail, name="requisition_detail"),
    path("meus-pedidos/", views.user_orders, name="user_orders"),
    path(
        "confirmar-recebimento/<int:order_id>/",
        views.confirmar_recebimento,
        name="confirmar_recebimento"
    ),

    # ====================
    # CARRINHO (LISTA)
    # ====================
    path("lista/", views.cart_view, name="cart_view"),
    path("lista/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("lista/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("lista/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("lista/enviar/", views.cart_submit, name="cart_submit"),

    # ====================
    # AUSTIN (PAINEL INTERNO)
    # ====================
    path("xodo-admin/", views.admin_home, name="admin_home"),
    path("xodo-admin/pedidos/", views.order_list, name="order_list"),
    path(
        "xodo-admin/pedidos/<int:order_id>/<str:new_status>/",
        views.update_order_status,
        name="update_order_status"
    ),

    # ====================
    # DJANGO ADMIN (SUPERUSUÁRIO)
    # ====================
    path("admin/", admin.site.urls),
]
