from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core import views

urlpatterns = [

    # Django Admin
    path("admin/", admin.site.urls),

    # Login comum do usuário
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Login do painel interno (setor / estoque)
    path("xodo-admin/login/", views.admin_login_view, name="admin_login"),

    # Painel do setor
    path("xodo-admin/", views.admin_home, name="admin_home"),
    path("xodo-admin/pedidos/", views.order_list, name="order_list"),
    path("xodo-admin/pedidos/<int:id>/pdf/", views.generate_pdf, name="generate_pdf"),
    path("xodo-admin/dashboard/", views.dashboard, name="dashboard"),

    # Teste PDF (Render)
    path("test-pdf/", views.test_pdf, name="test_pdf"),

    # Área do usuário comum
    path("", views.requisition_list, name="requisition_list"),
    path("requisition/<int:id>/", views.requisition_detail, name="requisition_detail"),
    path("send-order/<int:id>/", views.send_order, name="send_order"),
    path("pedido/enviado/", views.order_sent, name="order_sent"),
    path("meus-pedidos/", views.user_orders, name="user_orders"),

    path("order/preview/<int:id>/", views.order_preview, name="order_preview"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
