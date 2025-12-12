from django.db import models
from django.contrib.auth.models import User


class Requisition(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="requisitions/",
        blank=True,
        null=True
    )

    icon = models.ImageField(
        upload_to="icons/",
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

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    unit = models.CharField(max_length=20, default="un")

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_receive_orders", "Pode receber e gerenciar pedidos"),
        ]

    def __str__(self):
        return f"Pedido {self.id} - {self.requisition.name}"


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
