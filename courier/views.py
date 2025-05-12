from django.shortcuts import render,redirect
from .models import Product,Order,OrderUpdate,Contact,Profile,Pending_order,Shipping
from django.contrib.auth import login, authenticate,logout, update_session_auth_hash
from django.http import HttpResponse,HttpResponseRedirect
from .forms import SignUpForm,ProfileForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
#from django.db.models import Q
from django.db.models import Sum
import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.models import LogEntry
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse


# Employee/admin views disabled for client review
# pen_order = Pending_order.objects.all()
# pen_param = {'orders': pen_order}

def index(request):
    return render(request, 'courier/index.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('fname','') + " " + request.POST.get('lname','')
        email = request.POST.get('email', '')
        desc = request.POST.get('description', '')
        phone = request.POST.get('mobile', '')
        cont = Contact(name=name,description=desc,email=email,phone=phone)
        cont.save()
    return render(request, 'courier/contact.html')

@login_required
def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        try:
            # Initialize empty updates list
            updates = []
            most_update = None
            shipping = None
            error = None
            
            # Try to find order by order_id first
            order = Order.objects.filter(order_id=orderId)
            if len(order) > 0:
                updates = OrderUpdate.objects.filter(order_id=orderId).order_by('-time')
                most_update = updates.first()
                
                # Check if updates exist, if not, create a default update
                if not updates.exists():
                    order_obj = order.first()
                    if order_obj:
                        print(f"No updates found for order {orderId}, creating a default update")
                        default_update = OrderUpdate.objects.create(
                            order_id=orderId,
                            location=order_obj.receiver_address,
                            progress="Order has been placed",
                            status="Placed Order"
                        )
                        updates = OrderUpdate.objects.filter(order_id=orderId).order_by('-time')
                        most_update = updates.first()
            else:
                # Try to find a shipping with this tracking number
                try:
                    shipping = Shipping.objects.get(tracking_number=orderId)
                    # If found, redirect to appropriate shipping view or create a context for it
                    order_id = shipping.order.order_id
                    updates = OrderUpdate.objects.filter(order_id=order_id).order_by('-time')
                    most_update = updates.first()
                    
                    # Check if updates exist, if not, create a default update based on shipping
                    if not updates.exists():
                        print(f"No updates found for shipping {orderId}, creating a default update")
                        default_update = OrderUpdate.objects.create(
                            order_id=order_id,
                            location=shipping.order.receiver_address,
                            progress=f"Shipping status: {shipping.get_status_display()}",
                            status="Placed Order"
                        )
                        updates = OrderUpdate.objects.filter(order_id=order_id).order_by('-time')
                        most_update = updates.first()
                except Shipping.DoesNotExist:
                    # If neither order_id nor tracking_number is found
                    error = f"No order or shipment found with tracking number: {orderId}"
            
            # Create context with all necessary variables
            params = {
                'updates': updates, 
                'orderId': orderId,
                'most_update': most_update,
                'shipping': shipping,
                'error': error
            }
            
            return render(request, 'courier/tracker.html', params)
                
        except Exception as e:
            # Log the exception for debugging
            print(f"Error in tracker view: {str(e)}")
            return render(request, 'courier/tracker.html', 
                         {'error': "An error occurred while tracking your order. Please try again.",
                          'updates': []})  # Ensure updates is always provided
    
    # For GET requests, just render the empty form
    return render(request, 'courier/tracker.html', {'updates': []})  # Ensure updates is always provided


def order(request):
    products = Product.objects.all()
    params = {'product': products}
    if request.method == "POST":
        try:
            name = request.POST.get('s_name', '')
            email = request.POST.get('s_email', '')
            address = request.POST.get('s_address', '')
            phone = request.POST.get('s_phone', '')
            r_name = request.POST.get('r_name', '')
            r_email = request.POST.get('r_email', '')
            r_address = request.POST.get('r_address', '')
            r_phone = request.POST.get('r_phone', '')
            product = request.POST.get('product', '')
            weight = request.POST.get('weight','0.0')
            quantity = request.POST.get('quantity', '1.0')
            description = request.POST.get('other-info','')

            # Create and save the order
            order1 = Order(
                sender_name=name,
                sender_email=email,
                sender_address=address,
                sender_phone=phone,
                receiver_name=r_name,
                receiver_email=r_email,
                receiver_address=r_address,
                receiver_phone=r_phone,
                weight=weight,
                quantity=quantity,
                description=description,
                product_name=product
            )
            order1.save()

            # Create order update
            update = OrderUpdate(
                order_id=order1.order_id,
                location="-------",
                progress="The order has been placed"
            )
            update.save()

            # Create pending order
            pending = Pending_order(order_id=order1.order_id)
            pending.save()

            # Get the order ID for the thank you page
            id = order1.order_id

            # Add today's date to context
            from django.utils import timezone
            context = {
                'id': id,
                'today': timezone.now()
            }

            return render(request, 'courier/thank.html', context)
        except Exception as e:
            # Log the error and show an error message
            print(f"Error processing order: {str(e)}")
            params['error'] = "There was an error processing your order. Please try again."
            return render(request, 'courier/order.html', params)

    return render(request, 'courier/order.html', params)


def productView(request):
    products = Product.objects.all()
    params = {'product': products}
    return render(request, 'courier/product.html', params)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request,user)
            u = User.objects.get(username=username)
            u1 = Profile.objects.get(user=u)
            # For client review, only allow customer signup
            # Admin/employee functionality disabled
            # if request.user.is_superuser or u1.user_type == 'Admin':
            #     return redirect('/admin/')
            if u1.user_type == 'Customer':
                return redirect('/')
            else:
                # Redirect all non-customers to home for client review version
                return redirect('/')

    else:
        form = SignUpForm()
        profile_form = ProfileForm()
    return render(request, 'courier/signup.html', {'form': form , 'profile_form': profile_form})


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                # Get the user and profile after authentication
                try:
                    u1 = Profile.objects.get(user=user)
                    # Admin/employee functionality disabled for client review
                    # if request.user.is_superuser or u1.user_type == 'Admin':
                    #    return redirect('/admin/')
                    if u1.user_type == 'Customer':
                        return redirect('/')
                    # if u1.user_type == 'Permitted_Employee':
                    #     return redirect('/emp_home')
                    else:
                        return redirect('/')
                except Profile.DoesNotExist:
                    # If no profile exists but user is superuser
                    # if request.user.is_superuser:
                    #     return redirect('/admin/')
                    return redirect('/')
            else:
                messages.error(request, 'Your account has been disabled..!')
                return render(request, 'courier/login.html')
        else:
            messages.error(request, 'Invalid login..!')
            return render(request, 'courier/login.html')
    else:
        return render(request, 'courier/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def change_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
        return redirect('/login')
    else:
        return render(request,'courier/change_password.html')

# Employee/admin-only views commented out for client review
"""
def emp_index(request):
    pen_order = Pending_order.objects.all()
    params = {'orders': pen_order}
    return render(request, 'courier/emp_index.html',params)


def pending_order(request, order_id):
    pen_order = Pending_order.objects.all()
    pending_order_details = Order.objects.filter(order_id=order_id).all().last()
    params = {'orders': pen_order, 'pending_order_details': pending_order_details}
    return render(request, 'courier/pending_order.html', params)


def add_order(request):
    products = Product.objects.all()
    params = {'product': products,'orders': pen_order}
    if request.method == "POST":
        name = request.POST.get('s_name', '')
        address = request.POST.get('s_address', '')
        phone = request.POST.get('s_phone', '')
        r_name = request.POST.get('r_name', '')
        r_address = request.POST.get('r_address', '')
        r_phone = request.POST.get('r_phone', '')
        product_name = request.POST.get('product_name', '')
        weight = request.POST.get('weight','0.0')
        quantity = request.POST.get('quantity', '1.0')
        price = request.POST.get('price', '0.0')
        description = request.POST.get('other-info','')
        order1 = Order(sender_name=name, sender_address=address,
                       sender_phone=phone,receiver_name=r_name,
                       receiver_address=r_address,receiver_phone=r_phone,weight=weight,
                       quantity=quantity,description=description,product_name=product_name,price=price)
        order1.save()
        update = OrderUpdate(order_id=order1.order_id,
                             location="-------",
                             progress="The order has been placed")
        update.save()
        pending = Pending_order(order_id=order1.order_id)
        pending.save()
        id = order1.order_id
        param = {'id': id, 'orders': pen_order}
        return render(request, 'courier/thank.html', param)

    return render(request, 'courier/add_order.html', params)


def voucher(request):
    return render(request,'courier/voucher.html',pen_param)

def update_order(request):
    if request.method =="POST":
        order_id = request.POST.get('order_id', '')
        order_desc = request.POST.get('updateOption', '')
        location = request.POST.get('address', '')
        update = OrderUpdate(order_id=order_id,
                             location=location,
                             progress=order_desc,
                             status=order_desc)
        update.save()
        try:
            pending = Pending_order.objects.get(order_id=order_id)
            if order_desc != 'Delivered Product':
                obj = pending
                obj.save()
            else:
                obj = pending
                obj.delete()
        except Exception as e:
            print(e)
        return redirect('/emp_home')


def report(request):
    reports = Order.objects.values('dateTime') \
        .annotate(total_price=Sum('price')).order_by()

    params = {'orders': pen_order, 'report': reports}
    return render(request, 'courier/report.html', params)
"""

def thank(request):
    return render(request, 'courier/thank.html')

def check_order_updates(request, order_id=None):
    """
    Administrative utility function to check order updates and fix any issues.
    This can be disabled in production by removing the URL pattern.
    """
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized. Administrator access required.", status=403)
    
    # If no order_id provided, show all orders with their update counts
    if not order_id:
        orders = Order.objects.all().order_by('-dateTime')
        order_data = []
        
        for order in orders:
            updates_count = OrderUpdate.objects.filter(order_id=order.order_id).count()
            shipping_count = Shipping.objects.filter(order=order).count()
            order_data.append({
                'order_id': order.order_id,
                'sender': order.sender_name,
                'receiver': order.receiver_name,
                'date': order.dateTime,
                'updates_count': updates_count,
                'shipping_count': shipping_count
            })
            
        return render(request, 'courier/admin_utilities/check_updates.html', {
            'orders': order_data
        })
    
    # If order_id provided, show details for that specific order
    try:
        order = Order.objects.get(order_id=order_id)
        updates = OrderUpdate.objects.filter(order_id=order_id).order_by('-time')
        shippings = Shipping.objects.filter(order=order)
        
        # Check for missing updates
        if not updates.exists() and request.GET.get('fix', ''):
            # Create a default update
            OrderUpdate.objects.create(
                order_id=order_id,
                location=order.receiver_address,
                progress="Order has been placed (auto-created)",
                status="Placed Order"
            )
            updates = OrderUpdate.objects.filter(order_id=order_id).order_by('-time')
        
        return render(request, 'courier/admin_utilities/order_updates.html', {
            'order': order,
            'updates': updates,
            'shippings': shippings
        })
    
    except Order.DoesNotExist:
        return HttpResponse(f"Order with ID {order_id} not found.", status=404)

@staff_member_required
def add_order_update(request):
    """
    Handle adding a new order update from the admin utility page.
    This ensures updates are correctly associated with the order ID.
    """
    if request.method == 'POST':
        order_id = request.POST.get('order_id', '')
        status = request.POST.get('status', '')
        location = request.POST.get('location', '')
        progress = request.POST.get('progress', '')
        
        # Validate the data
        if not order_id or not status:
            messages.error(request, "Order ID and Status are required.")
            return redirect('check_order_updates', order_id=order_id)
            
        try:
            # Verify the order exists
            order = Order.objects.get(order_id=order_id)
            
            # Create the new order update
            update = OrderUpdate.objects.create(
                order_id=order_id,
                status=status,
                location=location,
                progress=progress
            )
            
            messages.success(request, f"Order update added successfully. Update ID: {update.update_id}")
            
        except Order.DoesNotExist:
            messages.error(request, f"Order with ID {order_id} does not exist.")
        except Exception as e:
            messages.error(request, f"Error adding order update: {str(e)}")
            
        return redirect('check_order_updates', order_id=order_id)
        
    # If not POST, redirect to the order list
    return redirect('check_order_updates')

@staff_member_required
def clear_admin_actions(request, order_id=None):
    """
    Clear all admin-added order updates, either for a specific order or all orders.
    This helps remove test data or reset order status information.
    """
    # Keep track of what was deleted
    deleted_count = 0
    
    try:
        if order_id:
            # For a specific order, keep only the initial "placed" update if it exists
            # First, check if there's an initial update
            initial_update = OrderUpdate.objects.filter(
                order_id=order_id, 
                status='Placed Order',
                progress__contains='placed'
            ).order_by('time').first()
            
            # Get all updates for this order
            updates = OrderUpdate.objects.filter(order_id=order_id)
            deleted_count = updates.count()
            
            # Delete all updates for this order
            updates.delete()
            
            # If we had an initial update, recreate it
            if initial_update:
                OrderUpdate.objects.create(
                    order_id=order_id,
                    status='Placed Order',
                    location=initial_update.location,
                    progress="Order has been placed (system restored)"
                )
                deleted_count -= 1  # Adjust count since we restored one
                
            messages.success(request, f"Cleared {deleted_count} updates for order #{order_id}.")
            return redirect('check_order_updates', order_id=order_id)
        else:
            # Clear updates for all orders, but preserve initial updates
            orders = Order.objects.all()
            for order in orders:
                # Find initial update for this order
                initial_update = OrderUpdate.objects.filter(
                    order_id=order.order_id, 
                    status='Placed Order',
                    progress__contains='placed'
                ).order_by('time').first()
                
                # Count and delete all updates
                order_updates = OrderUpdate.objects.filter(order_id=order.order_id)
                deleted_count += order_updates.count()
                order_updates.delete()
                
                # Recreate initial update
                OrderUpdate.objects.create(
                    order_id=order.order_id,
                    status='Placed Order',
                    location=order.receiver_address,
                    progress="Order has been placed (system restored)"
                )
                deleted_count -= 1  # Adjust count for each recreated initial update
            
            messages.success(request, f"Cleared {deleted_count} admin updates across all orders.")
            return redirect('check_order_updates')
            
    except Exception as e:
        messages.error(request, f"Error clearing updates: {str(e)}")
        if order_id:
            return redirect('check_order_updates', order_id=order_id)
        else:
            return redirect('check_order_updates')

# Admin utility views
@staff_member_required
def hover_test(request):
    """Test page for admin hover effects"""
    return render(request, 'courier/admin_utilities/hover_test.html')

@staff_member_required
@ensure_csrf_cookie
@require_http_methods(["POST"])
def delete_admin_log_view(request):
    """
    View to delete all admin log entries - either for current user or all users
    """
    try:
        delete_all = request.GET.get('all', 'false').lower() == 'true'
        
        # Log request information
        print(f"Delete log request from {request.user.username}, delete_all={delete_all}")
        print(f"Request method: {request.method}")
        print(f"Request GET params: {dict(request.GET)}")
        
        if delete_all and request.user.is_superuser:
            # Superusers can delete all log entries
            count_before = LogEntry.objects.count()
            deleted, details = LogEntry.objects.all().delete()
            print(f"Superuser {request.user.username} deleted ALL log entries ({deleted} total, count before: {count_before})")
        else:
            # Regular users can only delete their own logs
            count_before = LogEntry.objects.filter(user=request.user).count()
            deleted, details = LogEntry.objects.filter(user=request.user).delete()
            print(f"User {request.user.username} deleted {deleted} log entries (count before: {count_before})")
        
        # Check if client accepts HTML (form post redirect)
        accepts_html = 'text/html' in request.headers.get('Accept', '')
        
        # Ensure we're sending back a simple response
        response_data = {
            'status': 'success',
            'deleted_count': deleted,
            'count_before': count_before
        }
        
        # If client accepts HTML and this was a form submission, redirect back to admin
        if accepts_html and not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            messages.success(request, f"Successfully cleared {deleted} log entries.")
            return redirect('admin:index')
        
        # Otherwise return JSON
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Error deleting log entries for {request.user.username}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        # Check if client accepts HTML for error response
        if 'text/html' in request.headers.get('Accept', ''):
            messages.error(request, f"Error clearing log entries: {str(e)}")
            return redirect('admin:index')
            
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)