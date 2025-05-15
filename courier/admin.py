from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User, Group
from .models import Product, Order, OrderUpdate, Contact, Profile, Pending_order, Shipping

# Custom ModelAdmin classes

class ShippingAdmin(admin.ModelAdmin):
    list_display = ('shipping_id', 'order_link', 'tracking_number', 'carrier', 'status_colored',
                   'shipping_date', 'estimated_delivery', 'shipping_cost')
    list_filter = ('status', 'carrier', 'shipping_date')
    search_fields = ('tracking_number', 'order__order_id', 'carrier')
    readonly_fields = ('shipping_id',)
    fieldsets = (
        ('Shipping Information', {
            'fields': ('shipping_id', 'order', 'tracking_number', 'carrier', 'status', 'forward_no', 'customer', 'signed_by')
        }),
        ('Dates', {
            'fields': ('shipping_date', 'estimated_delivery', 'actual_delivery')
        }),
        ('Location Information', {
            'fields': ('origin', 'destination', 'no_of_pcs')
        }),
        ('Additional Information', {
            'fields': ('shipping_cost', 'notes')
        }),
    )

    def order_link(self, obj):
        url = f"/admin/courier/order/{obj.order.order_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.order.order_id)
    order_link.short_description = 'Shipment'

    def status_colored(self, obj):
        """
        Returns a colored status based on the shipping status.
        Uses a more flexible approach to handle various status values.
        """
        # Expanded color mapping with more status types
        colors = {
            # Standard statuses
            'pending': '#FFA500',    # Orange
            'in_transit': '#0000FF', # Blue
            'delivered': '#008000',  # Green
            'returned': '#FF0000',   # Red
            
            # Additional statuses that might be used
            'processing': '#9400D3',  # Purple
            'picked_up': '#4B0082',   # Indigo
            'out_for_delivery': '#4169E1',  # Royal Blue
            'failed_delivery': '#DC143C',   # Crimson
            'cancelled': '#696969',   # Dim Gray
            'on_hold': '#DAA520',     # Goldenrod
            'exception': '#B22222',   # FireBrick
        }
        
        # For case-insensitive matching
        status_lower = obj.status.lower()
        
        # Try direct match first
        if status_lower in colors:
            color = colors[status_lower]
        else:
            # Fallback to partial matching for similar statuses
            for key, value in colors.items():
                if key in status_lower:
                    color = value
                    break
            else:
                # Default if no match found
                color = '#000000'  # Black
        
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          color, obj.status)
    status_colored.short_description = 'Status'

    class Media:
        css = {
            'all': ('courier/css/admin.css',)
        }

class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'shipment_id_display', 'status', 'progress', 'custom_date', 'custom_time', 'location')
    list_filter = ('status', 'time')
    search_fields = ('order_id', 'progress', 'location')
    readonly_fields = ('update_id',)
    fieldsets = (
        ('Shipment Information', {
            'fields': ('update_id', 'order_id', 'status')
        }),
        ('Progress Information', {
            'fields': ('progress', 'location')
        }),
        ('Date and Time', {
            'fields': ('custom_date', 'custom_time')
        }),
    )
    
    def shipment_id_display(self, obj):
        return obj.order_id
    shipment_id_display.short_description = 'Shipment ID'

# Customize admin header, title and index title
admin.site.site_header = "Courier Management"
admin.site.site_title = "Courier Management" 
admin.site.index_title = "Administration"

# Register your models here.

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderUpdate, OrderUpdateAdmin)
admin.site.register(Contact)
admin.site.register(Profile)
admin.site.register(Pending_order)
admin.site.register(Shipping, ShippingAdmin)







