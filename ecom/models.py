from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_ADMIN    = 'admin'
    ROLE_CUSTOMER = 'customer'
    ROLE_CHOICES = [(ROLE_ADMIN,'Admin'),(ROLE_CUSTOMER,'Customer'),]

    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default=ROLE_CUSTOMER,)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name      = models.CharField(max_length=200)
    category  = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock     = models.PositiveIntegerField(default=0)
    price     = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPED   = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_SHIPPED,   'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    customer   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product    = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity   = models.PositiveIntegerField(default=1)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"