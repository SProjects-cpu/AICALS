from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # Customer-facing routes
    path("", views.index, name="home"),
    path("contact/", views.contact, name="contact"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    # path("productview/", views.productView, name="ProductView"),  # Removed Product view
    # path("order/",views.order,name="order"),  # Removed Order route
    path("login/",views.signin,name="login"),
    path("signup/",views.signup,name="signup"),
    path("logout/",views.user_logout,name="logout"),
    path("thank/",views.thank,name="thank"),
    path("change_password/",views.change_password,name="change_password"),

    # Admin utility routes
    path("admin/check_updates/", views.check_order_updates, name="check_order_updates"),
    path("admin/check_updates/<int:order_id>/", views.check_order_updates, name="check_order_updates"),
    path("admin/add_order_update/", views.add_order_update, name="add_order_update"),
    path("admin/clear_updates/", views.clear_admin_actions, name="clear_admin_actions"),
    path("admin/clear_updates/<int:order_id>/", views.clear_admin_actions, name="clear_admin_actions_for_order"),
    path("admin/hover_test/", views.hover_test, name="hover_test"),
    path('admin/clear_recent_actions/', admin_views.clear_recent_actions, name='clear_recent_actions'),
    
    # Custom admin action - using custom_admin prefix to avoid conflicts with Django admin URLs
    path('custom_admin/delete_log/', views.delete_admin_log_view, name='delete_admin_log'),

    # Employee/admin routes removed for client review
    # path("emp_home/",views.emp_index,name="emp_home"),
    # path("pending_order/<int:order_id>/",views.pending_order,name="pending_order"),
    # path("add_order/",views.add_order,name="add_order"),
    # path("voucher/",views.voucher,name="voucher"),
    # path("update_order/",views.update_order,name="update_order"),
    # path("report/",views.report,name="report"),
]