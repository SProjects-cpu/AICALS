from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.admin.models import LogEntry
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
import logging
from .models import Shipping, Order
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from datetime import timedelta
from django.core.paginator import Paginator
from django.conf import settings
from .models import OrderUpdate

# Get logger
logger = logging.getLogger(__name__)

@staff_member_required
def shipping_list_view(request):
    """
    Custom admin view to display shipping information
    """
    # Get current date for reporting
    today = timezone.now()

    # Get all shippings ordered by date
    shippings = Shipping.objects.all().order_by('-shipping_date')

    # Get counts for different statuses
    pending_count = Shipping.objects.filter(status='pending').count()
    in_transit_count = Shipping.objects.filter(status='in_transit').count()
    delivered_count = Shipping.objects.filter(status='delivered').count()
    returned_count = Shipping.objects.filter(status='returned').count()

    # Calculate total shipping cost
    total_shipping_cost = Shipping.objects.aggregate(total=Sum('shipping_cost'))['total'] or 0

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        shippings = shippings.filter(
            Q(tracking_number__icontains=search_query) |
            Q(carrier__icontains=search_query) |
            Q(order__order_id__icontains=search_query)
        )

    context = {
        'title': 'Shipping Management',
        'shippings': shippings,
        'has_permission': True,
        'site_header': 'Courier Management Administration',
        'site_title': 'Courier Management',
        'index_title': 'Shipping Management',
        'pending_count': pending_count,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'returned_count': returned_count,
        'total_count': shippings.count(),
        'total_shipping_cost': total_shipping_cost,
        'search_query': search_query,
        'today': today,
    }

    return render(request, 'admin/shipping_list.html', context)

@staff_member_required
@ensure_csrf_cookie
@require_http_methods(["POST"])
def delete_admin_log(request):
    """
    View to delete all admin log entries - either for current user or all users
    """
    try:
        delete_all = request.GET.get('all', 'false').lower() == 'true'
        
        # Log detailed request information for debugging
        logger.info(f"Delete log request from {request.user.username}, delete_all={delete_all}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request GET params: {dict(request.GET)}")
        logger.info(f"Request POST params: {dict(request.POST)}")
        
        if delete_all and request.user.is_superuser:
            # Superusers can delete all log entries
            count_before = LogEntry.objects.count()
            deleted, details = LogEntry.objects.all().delete()
            logger.info(f"Superuser {request.user.username} deleted ALL log entries ({deleted} total, count before: {count_before})")
        else:
            # Regular users can only delete their own logs
            count_before = LogEntry.objects.filter(user=request.user).count()
            deleted, details = LogEntry.objects.filter(user=request.user).delete()
            logger.info(f"User {request.user.username} deleted {deleted} log entries (count before: {count_before})")
        
        # Check if client accepts HTML (form post redirect)
        accepts_html = 'text/html' in request.headers.get('Accept', '')
        logger.info(f"Client accepts HTML: {accepts_html}")
        
        # Ensure we're sending back a simple response
        response_data = {
            'status': 'success',
            'deleted_count': deleted,
            'count_before': count_before
        }
        logger.info(f"Sending response: {response_data}")
        
        # If client accepts HTML and this was a form submission, redirect back to admin
        if accepts_html and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, f"Successfully cleared {deleted} log entries.")
            return redirect('admin:index')
        
        # Otherwise return JSON
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error deleting log entries for {request.user.username}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Check if client accepts HTML for error response
        if 'text/html' in request.headers.get('Accept', ''):
            messages.error(request, f"Error clearing log entries: {str(e)}")
            return redirect('admin:index')
            
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@staff_member_required
@require_POST
def clear_recent_actions(request):
    try:
        LogEntry.objects.filter(user_id=request.user.id).delete()
        return JsonResponse({'status': 'success', 'message': 'Recent actions cleared successfully.'})
    except Exception as e:
        # Log the exception for debugging
        logger = logging.getLogger(__name__)
        logger.error(f"Error clearing recent actions for user {request.user.id}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while clearing actions.'}, status=500)
