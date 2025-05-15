from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from enum import Enum, EnumMeta
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

# Configure logger
logger = logging.getLogger(__name__)


class UserType(Enum):
    Employee = 'Employee',
    Permitted_Employee = 'Permitted_Employee',
    Customer = 'Customer',
    Admin = 'Admin'


class Shipping(models.Model):
    shipping_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='shippings')
    tracking_number = models.CharField(max_length=50, unique=True)
    carrier = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')
    shipping_date = models.DateTimeField(default=datetime.now)
    estimated_delivery = models.DateTimeField(default=datetime.now)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    shipping_cost = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, null=True)
    forward_no = models.CharField(max_length=50, blank=True, null=True)
    customer = models.CharField(max_length=100, blank=True, null=True)
    signed_by = models.CharField(max_length=100, blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)
    no_of_pcs = models.IntegerField(default=1, blank=True, null=True)

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
    
    class Meta:
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'


class Pending_order(models.Model):
    pending_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Pending Shipment'
        verbose_name_plural = 'Pending Shipments'


# Custom OrderStatus class that works with migration files
class OrderStatusMeta(EnumMeta):
    def __call__(cls, value, *args, **kwargs):
        # Handle tuple values like ('Placed Order',)
        if isinstance(value, tuple) and len(value) > 0:
            value = value[0]
        
        # Try to find an exact match first
        try:
            return super().__call__(value, *args, **kwargs)
        except ValueError:
            # For migration compatibility, create a dummy member
            # This member won't be in the actual enum but will be returned for this call
            # Create a dummy enum member by manually instantiating
            dummy = object.__new__(OrderStatus)
            dummy._name_ = f"UNKNOWN_{str(value).replace(' ', '_').upper()}"
            dummy._value_ = value
            return dummy


class OrderStatus(Enum, metaclass=OrderStatusMeta):
    # Current values with new names
    placed = 'Placed Shipment',
    confirmed = 'Confirmed Shipment',
    picked_up = 'Picked-up',
    dispatched = 'Dispatched Product',
    reached = 'Reached Product',
    delivered = 'Delivered Product'
    
    # Old values for migration compatibility
    PLACED_ORDER = 'Placed Order',
    CONFIRMED_ORDER = 'Confirmed Order',
    PICKED_UP = 'Picked-up',
    DISPATCHED_PRODUCT = 'Dispatched Product',
    REACHED_PRODUCT = 'Reached Product',
    DELIVERED_PRODUCT = 'Delivered Product'
    
    def __str__(self):
        if isinstance(self._value_, tuple) and len(self._value_) > 0:
            return str(self._value_[0])
        return str(self._value_)


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default=0)
    progress = models.CharField(max_length=5000, default="Order status updated")
    time = models.DateTimeField(auto_now_add=True)
    custom_date = models.CharField(max_length=50, blank=True, null=True, help_text="Format: Day, Date Month, Year (e.g., Tue, 13 Jan, 2025)")
    custom_time = models.CharField(max_length=20, blank=True, null=True, help_text="Format: HH:MM AM/PM (e.g., 02:30 PM)")
    location = models.CharField(max_length=150)
    status = models.CharField(max_length=50,
                              choices=[('Placed Order', _('Placed Shipment')), ('Confirmed Order', _('Confirmed Shipment')),
                                       ('Picked-up', _('Picked-up')), ('Dispatched Product', _('Dispatched Product')),
                                       ('Reached Product', _('Reached Product')),
                                       ('Delivered Product', _('Delivered Product')),
                                       ], default='Placed Order')

    def __str__(self):
        return str(self.update_id) + " Shipment Id(" + str(self.order_id) + ")"
        
    class Meta:
        verbose_name = 'Shipment Update'
        verbose_name_plural = 'Shipment Updates'


@receiver(post_save, sender=Shipping)
def update_order_status(sender, instance, created, **kwargs):
    """
    Update OrderUpdate when Shipping status changes.
    
    This signal handler maps shipping status to order status and creates
    appropriate OrderUpdate records to track the progress of an order.
    
    Args:
        sender: The model class (Shipping)
        instance: The Shipping instance that triggered the signal
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments
    """
    try:
        # Map Shipping status to OrderUpdate status
        # Use case-insensitive match for common statuses
        status_lower = instance.status.lower()
        if 'pending' in status_lower:
            shipping_status = 'Placed Order'
        elif 'transit' in status_lower or 'pick' in status_lower or 'ship' in status_lower:
            shipping_status = 'Dispatched Product'
        elif 'deliver' in status_lower:
            shipping_status = 'Delivered Product'
        elif 'return' in status_lower:
            shipping_status = 'Reached Product'
        else:
            # For custom status values, default to a generic status
            shipping_status = 'Placed Order'
            logger.info(f"Unknown shipping status '{instance.status}' mapped to 'Placed Order'")
        
        order_id = instance.order.order_id
        
        # For new shipments, always add an order update
        if created:
            logger.info(f"Creating new OrderUpdate for new shipping #{instance.shipping_id}")
            update = OrderUpdate.objects.create(
                order_id=order_id,
                progress=f"New shipment created with tracking number: {instance.tracking_number}",
                location=instance.order.receiver_address,
                status=shipping_status
            )
            logger.info(f"Created OrderUpdate #{update.update_id} for order #{order_id}")
        else:
            # Check if most recent order update has a different status
            latest_update = OrderUpdate.objects.filter(order_id=order_id).order_by('-time').first()
            
            # If no updates exist or the status is different, create a new one
            if not latest_update or latest_update.status != shipping_status:
                logger.info(f"Creating new OrderUpdate for shipping status change: {instance.status}")
                update = OrderUpdate.objects.create(
                    order_id=order_id,
                    progress=f"Shipping status updated: {instance.status}",
                    location=instance.order.receiver_address,
                    status=shipping_status
                )
                logger.info(f"Created OrderUpdate #{update.update_id} for order #{order_id}")
            
        # Ensure there's at least one order update for this order
        updates_count = OrderUpdate.objects.filter(order_id=order_id).count()
        if updates_count == 0:
            logger.info(f"No updates found for order #{order_id}, creating default update")
            OrderUpdate.objects.create(
                order_id=order_id,
                progress=f"Order status: {instance.status}",
                location=instance.order.receiver_address,
                status=shipping_status
            )
    except Exception as e:
        # Log the error but don't re-raise to avoid breaking the save operation
        logger.error(f"Error updating order status from shipping: {str(e)}")

