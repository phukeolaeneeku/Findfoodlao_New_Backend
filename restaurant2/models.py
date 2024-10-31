from django.db import models
from users.models import UserModel
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from django.db import transaction

from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Sum, F, DecimalField, Q

class Restaurant(models.Model):
    restaurant = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, verbose_name="Restaurant owner"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Restaurant name",
    )
    logo = models.FileField(
        null=True, blank=True, verbose_name="Logo", upload_to="media/restaurant/"
    )
    address = models.CharField(
        max_length=200,
        verbose_name="Restaurant location",
    )
    banner_image = models.FileField(
        null=True,
        blank=True,
        verbose_name="Banner image",
        upload_to="media/restaurant/",
    )
    phone = models.CharField(
        max_length=15,
        null=True, blank=True,
        verbose_name="Phone number"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Introduction")
    time = models.CharField(
        max_length=50,
        verbose_name="Opening time",
        null=True, blank=True
    )
    
    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
        indexes = [
            models.Index(fields=['name'], name='name_idx'),
            models.Index(fields=['address'], name='address_idx'),
        ]

    def __str__(self):
        return f"ID: {self.id} || name: {self.name} owned by {self.restaurant}"



class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category name")
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="categories"
    )

    def __str__(self):
        return f"{self.name} from => {self.restaurant.name}"


class Employee(models.Model):
    ROLE_CHOICES = [
        ("COUNTER", "Counter"),
        ("WAITER", "Waiter"),
    ]

    employee = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, verbose_name="Restaurant employee"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Employee name",
    )
    phone = models.CharField(max_length=125, verbose_name="Phone number")
    address = models.CharField(max_length=200)
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="employees"
    )
    role = models.CharField(
        max_length=100, verbose_name="Role", choices=ROLE_CHOICES, default="COUNTER"
    )

    def __str__(self):
        return f"{self.employee.email} is an employ from {self.restaurant}"


class Table(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name="Restaurant",
        related_name="tables",
    )
    number = models.PositiveIntegerField()
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True)

    def save(self, *args, **kwargs):
        # Determine if the instance is being created for the first time
        creating = self.pk is None
        super().save(*args, **kwargs)
        
        if creating:
            # Generate the QR code using the assigned ID
            qr_url = f"http://43.201.1.227/home/restaurant/{self.restaurant.id}/table/{self.id}"
            qr = qrcode.make(qr_url)
            qr_io = BytesIO()
            qr.save(qr_io, "PNG")
            qr_file = File(qr_io, name=f"{self.id}.png")
            
            # Save the QR code image
            self.qr_code.save(f"{self.id}.png", qr_file, save=False)
            
            # Save the instance again to update the qr_code field
            super().save(update_fields=['qr_code'])

    def _str_(self):
        return f"Restaurant: {self.restaurant.name} - Table: {self.number}"

    def is_available(self):
        return not self.orders.filter(status__in=["PENDING", "PREPARING"]).exists()


class Point(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="points")
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="points"
    )
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} points for {self.user.email} at {self.restaurant.name} on {self.timestamp}"

    class Meta:
        ordering = ["-timestamp"]

    @staticmethod
    def add_points(user, restaurant, amount):
        Point.objects.create(user=user, restaurant=restaurant, amount=amount)

    @staticmethod
    def spend_points(user, restaurant, amount):
        if user.get_total_points(restaurant) >= amount:
            Point.objects.create(user=user, restaurant=restaurant, amount=-amount)
            return True
        return False


class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name="Restaurant",
        related_name="menu_items",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Category",
    )
    image = models.FileField(
        null=True,
        blank=True,
        verbose_name="Image",
        upload_to="media/restaurant/MenuItem",
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Restaurant: {self.restaurant.name} - Menu item: {self.name}"

class OrderQuerySet(models.QuerySet):
    def unpaid(self):
        return self.filter(paid=False)

    def by_status(self, status):
        return self.filter(order_items__status=status).distinct()

    def by_statuses(self, statuses):
        return self.filter(order_items__status__in=statuses).distinct()

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db).select_related(
            'restaurant', 'table', 'user', 'employee'
        ).prefetch_related('order_items__menu_item')

    def unpaid(self):
        return self.get_queryset().unpaid()

    def by_status(self, status):
        return self.get_queryset().by_status(status)

    def by_statuses(self, statuses):
        return self.get_queryset().by_statuses(statuses)

class Order(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name="Restaurant",
        related_name="orders",
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="orders",
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Employee",
        related_name="orders",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    objects = OrderManager()

    class Meta:
        indexes = [
            models.Index(fields=["restaurant"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["paid"]),
        ]

    def get_total_cost(self):
        return self.order_items.filter(~Q(status='CANCELLED')).aggregate(
            total_cost=Sum(F('menu_item__price') * F('quantity'), output_field=DecimalField())
        )['total_cost'] or 0

    def __str__(self):
        table_number = self.table.number if self.table else "N/A"
        return f"Order {self.id} at Table {table_number}"

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PREPARING", "Preparing"),
        ("READY", "Ready"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Employee",
        related_name="order_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError('Quantity must be positive.')

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for Order {self.order.id}"

class OrderStatusHistory(models.Model):
    order_item = models.ForeignKey(
        OrderItem, related_name="status_history", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=OrderItem.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OrderItem {self.order_item.id} changed to {self.status} at {self.timestamp}"