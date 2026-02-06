from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    """
    Representa uma filial (ex: Queimados, Austin)
    """
    name = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Perfil do usuário ligado a uma filial
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.ForeignKey(Location, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.username} - {self.location.name}"


class Product(models.Model):
    """
    Produto base do sistema
    (mantive simples, ajusta se já tiver algo mais completo)
    """
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Pedido interfilial:
    Queimados -> Austin
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


class OrderItem(models.Model):
    """
    Itens do pedido
    """
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


class OrderStatusHistory(models.Model):
    """
    Histórico de mudança de status do pedido
    ESSENCIAL para cálculo de tempo
    """
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
