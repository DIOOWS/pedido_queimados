from django.core.management.base import BaseCommand
from core.models import Requisition, Product

class Command(BaseCommand):
    help = "Remove referências antigas de imagens locais (/media/)"

    def handle(self, *args, **kwargs):
        count = 0

        for req in Requisition.objects.all():
            if req.image and str(req.image).startswith("icons/"):
                req.image = None
                req.save()
                count += 1

            if req.icon and str(req.icon).startswith("icons/"):
                req.icon = None
                req.save()
                count += 1

        for prod in Product.objects.all():
            if prod.image and str(prod.image).startswith("products/"):
                prod.image = None
                prod.save()
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f"{count} imagens antigas removidas com sucesso.")
        )
