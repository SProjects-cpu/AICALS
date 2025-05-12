from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from enum import Enum
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserType(Enum):
    Employee = 'Employee',
    Permitted_Employee = 'Permitted_Employee',
    Customer = 'Customer',
    Admin = 'Admin'


class Shipping(models.Model):
    SHIPPING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ]

    shipping_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='shippings')
    tracking_number = models.CharField(max_length=50, unique=True)
    carrier = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES, default='pending')
    shipping_date = models.DateTimeField(default=datetime.now)
    estimated_delivery = models.DateTimeField(default=datetime.now)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Shipping #{self.shipping_id} - {self.tracking_number}"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20,  choices=[('Employee', _('Employee')),('Permitted_Employee', _('Permitted_Employee')),
                                                          ('Customer', _('Customer')),('Admin', _('Admin'))],)
    address = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    product_name = models.CharField(max_length=50)
    product_Description = models.CharField(max_length=300)
    product_type = models.CharField(max_length=100)
    product_image = models.ImageField(upload_to='courier/images', default="")
    product_weight = models.FloatField()
    product_price = models.FloatField()

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    name = models.CharField(max_length=70)
    description = models.CharField(max_length=300)
    email = models.EmailField(max_length=111, default="")
    phone = models.CharField(max_length=12, default="")

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    sender_name = models.CharField(max_length=90)
    sender_email = models.EmailField(max_length=111, default="")
    sender_address = models.CharField(max_length=111)
    sender_phone = models.CharField(max_length=111, default="")
    receiver_name = models.CharField(max_length=90)
    receiver_email = models.EmailField(max_length=111, default="")
    receiver_address = models.CharField(max_length=111)
    receiver_phone = models.CharField(max_length=111, default="")
    product_name = models.CharField(max_length=111)
    weight = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    quantity = models.FloatField(default=1.0)
    description = models.CharField(max_length=300, default="")
    dateTime = models.DateTimeField(default=datetime.now, blank=True)
    expectedDate = models.DateTimeField(default=datetime.now, blank=True)


class Pending_order(models.Model):
    pending_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    time = models.DateTimeField(auto_now_add=True)


class OrderStatus(Enum):
    placed = 'Placed Order',
    confirmed = 'Confirmed Order',
    picked_up = 'Picked-up',
    dispatched = 'Dispatched Product',
    reached = 'Reached Product',
    delivered = 'Delivered Product'


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default=0)
    progress = models.CharField(max_length=5000, default="Order status updated")
    time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=150)
    status = models.CharField(max_length=50,
                              choices=[('Placed Order', _('Placed Order')), ('Confirmed Order', _('Confirmed Order')),
                                       ('Picked-up', _('Picked-up')), ('Dispatched Product', _('Dispatched Product')),
                                       ('Reached Product', _('Reached Product')),
                                       ('Delivered Product', _('Delivered Product')),
                                       ], default='Placed Order')

    def __str__(self):
        return str(self.update_id) + " Order Id(" + str(self.order_id) + ")"


@receiver(post_save, sender=Shipping)
def update_order_status(sender, instance, created, **kwargs):
    """
    Update OrderUpdate when Shipping status changes
    """
    try:
        # Map Shipping status to OrderUpdate status
        order_status_map = {
            'pending': 'Placed Order',
            'in_transit': 'Dispatched Product',
            'delivered': 'Delivered Product',
            'returned': 'Reached Product',  # Using Reached Product for returns
        }
        
        order_id = instance.order.order_id
        shipping_status = order_status_map.get(instance.status, 'Placed Order')
        
        # For new shipments, always add an order update
        if created:
            print(f"Creating new OrderUpdate for new shipping #{instance.shipping_id}")
            update = OrderUpdate.objects.create(
                order_id=order_id,
                progress=f"New shipment created with tracking number: {instance.tracking_number}",
                location=instance.order.receiver_address,
                status=shipping_status
            )
            print(f"Created OrderUpdate #{update.update_id} for order #{order_id}")
        else:
            # Check if most recent order update has a different status
            latest_update = OrderUpdate.objects.filter(order_id=order_id).order_by('-time').first()
            
            # If no updates exist or the status is different, create a new one
            if not latest_update or latest_update.status != shipping_status:
                print(f"Creating new OrderUpdate for shipping status change: {instance.status}")
                update = OrderUpdate.objects.create(
                    order_id=order_id,
                    progress=f"Shipping status updated: {instance.get_status_display()}",
                    location=instance.order.receiver_address,
                    status=shipping_status
                )
                print(f"Created OrderUpdate #{update.update_id} for order #{order_id}")
            
        # Ensure there's at least one order update for this order
        updates_count = OrderUpdate.objects.filter(order_id=order_id).count()
        if updates_count == 0:
            print(f"No updates found for order #{order_id}, creating default update")
            OrderUpdate.objects.create(
                order_id=order_id,
                progress=f"Order status: {instance.get_status_display()}",
                location=instance.order.receiver_address,
                status=shipping_status
            )
    except Exception as e:
        print(f"Error updating order status from shipping: {str(e)}")

