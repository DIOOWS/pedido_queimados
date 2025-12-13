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
    # USUÁRIO
    # ====================
    path("", views.requisition_list, name="requisition_list"),
    path("requisition/<int:id>/", views.requisition_detail, name="requisition_detail"),
    path("requisition/<int:id>/send/", views.send_order, name="send_order"),
    path("meus-pedidos/", views.user_orders, name="user_orders"),
    path("pedido-enviado/", views.order_sent, name="order_sent"),
    path("pedido/<int:id>/preview/", views.order_preview, name="order_preview"),

    # ====================
    # ADMIN / SETOR
    # ====================
    path("xodo-admin/login/", views.admin_login_view, name="admin_login"),
    path("xodo-admin/", views.admin_home, name="admin_home"),
    path("xodo-admin/pedidos/", views.order_list, name="order_list"),
    path("xodo-admin/dashboard/", views.dashboard, name="dashboard"),
    path("xodo-admin/pedidos/<int:id>/pdf/", views.generate_pdf, name="generate_pdf"),

    # ====================
    # TESTE PDF
    # ====================
    path("test-pdf/", views.test_pdf),

    # ====================
    # DJANGO ADMIN
    # ====================
    path("admin/", admin.site.urls),
]
