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
    # HOME (redireciona por filial)
    # ====================
    path("", views.home, name="home"),

    # ====================
    # QUEIMADOS (REQUISIÇÕES + PRODUTOS)
    # ====================
    path("requisicoes/", views.requisition_list, name="requisition_list"),
    path("requisition/<int:id>/", views.requisition_detail, name="requisition_detail"),

    # ====================
    # QUEIMADOS (CARRINHO)
    # ====================
    path("lista/", views.cart_view, name="cart_view"),
    path("lista/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("lista/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("lista/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("lista/enviar/", views.cart_submit, name="cart_submit"),
    path("pedido-enviado/", views.order_sent, name="order_sent"),

    # ====================
    # QUEIMADOS (MEUS PEDIDOS / CONFIRMA RECEBIMENTO)
    # ====================
    path("meus-pedidos/", views.user_orders, name="user_orders"),
    path("confirmar-recebimento/<int:id>/", views.confirmar_recebimento, name="confirmar_recebimento"),

    # ====================
    # AUSTIN (ADMIN XODÓ)
    # ====================
    path("xodo-admin/", views.admin_home, name="admin_home"),
    path("xodo-admin/avancar/<int:id>/", views.advance_status, name="advance_status"),

    # ====================
    # DJANGO ADMIN (só pra superuser/staff)
    # ====================
    path("admin/", admin.site.urls),
]
