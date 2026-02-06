from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("requisicoes/", views.requisition_list, name="requisition_list"),
    path("requisition/<int:id>/", views.requisition_detail, name="requisition_detail"),

    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/submit/", views.cart_submit, name="cart_submit"),

    path("meus-pedidos/", views.user_orders, name="user_orders"),
    path("pedido-enviado/", views.order_sent, name="order_sent"),

    path("xodo-admin/", views.admin_home, name="admin_home"),
    path("xodo-admin/avancar/<int:id>/", views.advance_status, name="advance_status"),
]
