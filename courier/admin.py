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
            'fields': ('shipping_id', 'order', 'tracking_number', 'carrier', 'status')
        }),
        ('Dates', {
            'fields': ('shipping_date', 'estimated_delivery', 'actual_delivery')
        }),
        ('Additional Information', {
            'fields': ('shipping_cost', 'notes')
        }),
    )

    def order_link(self, obj):
        url = f"/admin/courier/order/{obj.order.order_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.order.order_id)
    order_link.short_description = 'Order'

    def status_colored(self, obj):
        colors = {
            'pending': '#FFA500',  # Orange
            'in_transit': '#0000FF',  # Blue
            'delivered': '#008000',  # Green
            'returned': '#FF0000',  # Red
        }
        color = colors.get(obj.status, '#000000')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status_colored.short_description = 'Status'

    class Media:
        css = {
            'all': ('courier/css/admin.css',)
        }

class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'order_id', 'status', 'progress', 'time', 'location')
    list_filter = ('status', 'time')
    search_fields = ('order_id', 'progress', 'location')
    readonly_fields = ('update_id',)
    fieldsets = (
        ('Order Information', {
            'fields': ('update_id', 'order_id', 'status')
        }),
        ('Progress Information', {
            'fields': ('progress', 'location')
        }),
    )

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







