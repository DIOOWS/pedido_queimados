from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.username} - {self.location.name}"


class Requisition(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to="requisitions/", blank=True, null=True)
    icon = models.ImageField(upload_to="requisitions/icons/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.CASCADE,
        related_name="products"
    )
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.requisition.name} - {self.name}"


class Order(models.Model):
    class Status(models.TextChoices):
        CRIADO = "CRIADO", "Criado"
        RECEBIDO_DESTINO = "RECEBIDO_DESTINO", "Recebido pela filial destino"
        SEPARANDO = "SEPARANDO", "Separando"
        ENVIADO = "ENVIADO", "Enviado"
        RECEBIDO_ORIGEM = "RECEBIDO_ORIGEM", "Recebido pela filial origem"

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
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
        max_length=30,  # aumentei pra caber RECEBIDO_DESTINO/ORIGEM sem risco
        choices=Status.choices,
        default=Status.CRIADO
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class OrderStatusHistory(models.Model):
    """
    Histórico de status (para medir tempo: recebido -> enviado -> recebido origem)
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=30)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        ordering = ["changed_at"]

    def __str__(self):
        return f"Pedido {self.order.id} - {self.status} - {self.changed_at}"
