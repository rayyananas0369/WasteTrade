
from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "signup/",
        views.signup,
        name="signup"
    ),

    path(
        "signup-success/",
        views.signup_success,
        name="signup_success"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "customer-dashboard-preview/",
        views.customer_dashboard_preview,
        name="customer_dashboard_preview"
    ),

    path(
        "dealer-dashboard/",
        views.dealer_dashboard,
        name="dealer_dashboard"
    ),

    path(
        "add-waste-preview/",
        views.add_waste_preview,
        name="add_waste_preview"
    ),

    path(
        "my-listings/",
        views.my_listings,
        name="my_listings"
    ),

    path(
        "forgot-password/",
        views.forgot_password,
        name="forgot_password"
    ),

    path(
        "check-email/",
        views.check_email,
        name="check_email"
    ),

    path(
        "reset-password-preview/",
        views.reset_password_preview,
        name="reset_password_preview"
    ),
path(
    "admin-dashboard/",
    views.admin_dashboard,
    name="admin_dashboard",
),

path(
    "dealer/accept/<int:listing_id>/",
    views.dealer_accept_listing,
    name="dealer_accept_listing",
),
]
