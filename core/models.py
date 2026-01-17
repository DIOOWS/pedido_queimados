from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Requisition(models.Model):
    name = models.CharField(max_length=100, db_index=True)
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

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.CASCADE,
        related_name="products",
        db_index=True,
    )

    name = models.CharField(max_length=100, db_index=True)

    image = CloudinaryField(
        "product_image",
        folder="products"
    )

    unit = models.CharField(max_length=20, default="un")

    class Meta:
        # Evita produto repetido (mesmo nome) na mesma requisição
        constraints = [
            models.UniqueConstraint(
                fields=["requisition", "name"],
                name="uniq_product_per_requisition",
            )
        ]
        indexes = [
            models.Index(fields=["requisition", "name"]),
        ]

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        permissions = [
            ("can_receive_orders", "Pode receber e gerenciar pedidos"),
        ]
        indexes = [
            models.Index(fields=["is_read", "-created_at"]),    # não lidos recentes
            models.Index(fields=["user", "-created_at"]),       # meus pedidos recentes
            models.Index(fields=["requisition", "-created_at"]),# por requisição
        ]

    def __str__(self):
        return f"Pedido {self.id} - {self.requisition.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        # Evita o mesmo produto aparecer duas vezes no mesmo pedido
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="uniq_product_per_order",
            )
        ]
        indexes = [
            models.Index(fields=["order", "product"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
