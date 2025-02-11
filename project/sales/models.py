from django.db import models
from django.contrib.auth.models import User


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.CharField(max_length=20, default="sales", null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.CharField(max_length=255, null=True, blank=True)
    tel = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username


# 2. ข้อมูลลูกค้า
class Customer(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.first_name


# 3. ข้อมูลสินค้า
class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name


class SaleRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    STATUS_CHOICES = [
        ("pending", "รอคอนเฟิร์ม"),
        ("confirmed", "คอนเฟิร์มยอดแล้ว"),
    ]
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, blank=True, null=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True
    )
    quantity = models.IntegerField()
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    po_document = models.FileField(upload_to="po_documents/", blank=True, null=True)
    payment_slip = models.FileField(upload_to="payment_slips/", blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sale_records",
        blank=True,
        null=True,
    )

    def __str__(self):
        product_name = self.product.name if self.product else "No Product"
        return f"{self.customer} - {product_name}"
