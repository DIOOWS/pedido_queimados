from django.db import models
from django.contrib.auth.models import User


# =========================================================
# FILIAIS
# =========================================================
class Location(models.Model):
    """
    Representa uma filial (ex: Queimados, Austin)
    """
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


# =========================================================
# PERFIL DO USUÁRIO
# =========================================================
class UserProfile(models.Model):
    """
    Liga o usuário a uma filial
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.user.username} ({self.location.name})"


# =========================================================
# REQUISIÇÕES (SÓ PARA QUEIMADOS)
# =========================================================
class Requisition(models.Model):
    """
    Agrupador visual / categoria de produtos
    Ex: Mini Pizza, Empadão, Bolo, etc
    """
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="requisitions/", blank=True, null=True)
    icon = models.ImageField(upload_to="requisition_icons/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================================================
# PRODUTOS (PERTENCEM A UMA REQUISIÇÃO)
# =========================================================
class Product(models.Model):
    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.requisition.name} - {self.name}"


# =========================================================
# PEDIDO (QUEIMADOS → AUSTIN)
# =========================================================
class Order(models.Model):
    """
    Pedido interfilial
    """

    class Status(models.TextChoices):
        CRIADO = "CRIADO", "Criado"
        RECEBIDO = "RECEBIDO", "Recebido pela filial destino"
        SEPARANDO = "SEPARANDO", "Separando"
        ENVIADO = "ENVIADO", "Enviado"
        RECEBIDO_ORIGEM = "RECEBIDO_ORIGEM", "Recebido pela filial origem"

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders_created"
    )

    origin_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="orders_sent"
    )

    destination_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="orders_received"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CRIADO
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} ({self.origin_location} → {self.destination_location})"


# =========================================================
# ITENS DO PEDIDO
# =========================================================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# =========================================================
# HISTÓRICO DE STATUS (AUDITORIA)
# =========================================================
class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)

    changed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f"Pedido {self.order.id} - {self.status} - {self.changed_at}"
