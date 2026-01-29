from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Requisition(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    image = CloudinaryField(
        "requisition_image",
        folder="requisitions",
        blank=True,
        null=True
    )

    icon = CloudinaryField(
        "requisition_icon",
        folder="icons",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=100)

    image = CloudinaryField(
        "product_image",
        folder="products"
    )

    unit = models.CharField(max_length=20, default="un")

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        CONCLUIDO = "CONCLUIDO", "Concluído"

        # (pra sua próxima fase do fluxo, já deixo pronto)
        RECEBIDO_AUSTIN = "RECEBIDO_AUSTIN", "Recebido (Austin)"
        EM_SEPARACAO = "EM_SEPARACAO", "Em separação"
        ENVIADO = "ENVIADO", "Enviado"
        RECEBIDO_QUEIMADOS = "RECEBIDO_QUEIMADOS", "Recebido (Queimados)"

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # pedido pode conter itens de várias requisições
    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # se você ainda usa pra badge de "novo pedido", pode manter
    is_read = models.BooleanField(default=False)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDENTE
    )

    concluded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_receive_orders", "Pode receber e gerenciar pedidos"),
        ]

    def __str__(self):
        return f"Pedido {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


# =========================
# SETOR / LOCAL (Austin / Queimados)
# =========================

class Location(models.Model):
    name = models.CharField(max_length=60, unique=True)  # Austin / Queimados

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # ✅ IMPORTANTE: deixe null/blank para não quebrar usuários antigos
    # Depois você vai no admin e define Austin/Queimados para cada usuário.
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)

    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        loc = self.location.name if self.location else "Sem setor"
        return f"{self.user.username} - {loc}"
