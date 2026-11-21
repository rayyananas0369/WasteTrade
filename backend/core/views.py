
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as auth_login,
    logout as auth_logout,
)

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .forms import SignupForm, WasteItemForm, PickupForm
from .models import (
    UserProfile,
    WasteRate,
    WasteListing,
    WasteItem,
    WASTE_TYPE_DETAILS,
)
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from django.contrib.admin.views.decorators import staff_member_required


User = get_user_model()


# WASTETRADE CONDITION-BASED PRICING
# Admin WasteRate = base price for Clean / Dry waste

CONDITION_RATE_MULTIPLIERS = {
    "clean_dry": Decimal("1.00"),
    "mixed": Decimal("0.80"),
    "damaged": Decimal("0.60"),
}


# ==========================================
# CUSTOMER / BASKET HELPERS
# ==========================================

def is_customer(request):

    profile = getattr(
        request.user,
        "profile",
        None
    )

    return (
        profile is not None
        and profile.role == "customer"
    )


def get_draft(user):

    return (
        WasteListing.objects
        .filter(
            customer=user,
            status="draft"
        )
        .order_by("-created_at")
        .first()
    )


def update_listing_totals(listing):

    totals = listing.items.aggregate(
        total_weight=Sum("estimated_weight"),
        total_amount=Sum("estimated_amount"),
    )

    listing.estimated_weight = (
        totals["total_weight"] or Decimal("0.00")
    )

    listing.estimated_amount = (
        totals["total_amount"] or Decimal("0.00")
    )

    listing.save(
        update_fields=[
            "estimated_weight",
            "estimated_amount",
        ]
    )


# ==========================================
# HOME PAGE
# ==========================================

def home(request):

    return render(
        request,
        "core/home.html"
    )


# ==========================================
# CUSTOMER / DEALER SIGNUP
# ==========================================

def signup(request):

    if request.method == "GET":
        role = request.GET.get("type", "customer")
    else:
        role = request.POST.get("role", "customer")

    if role not in ("customer", "dealer"):
        role = "customer"

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            name_parts = (
                data["full_name"].strip().split(" ", 1)
            )

            first_name = name_parts[0]

            last_name = (
                name_parts[1]
                if len(name_parts) > 1
                else ""
            )

            try:

                with transaction.atomic():

                    # Django automatically hashes password

                    user = User.objects.create_user(
                        username=data["email"],
                        email=data["email"],
                        first_name=first_name,
                        last_name=last_name,
                        password=data["password1"],
                        is_active=(
                            data["role"] == "customer"
                        )
                    )

                    # Save customer/dealer details

                    UserProfile.objects.create(
                        user=user,
                        role=data["role"],
                        phone=data["phone"],
                        shop_name=data["shop_name"],
                        service_area=data["service_area"],
                        dealer_approved=False
                    )

            except IntegrityError:

                form.add_error(
                    "email",
                    "This email is already registered."
                )

            else:

                request.session["signup_role"] = (
                    data["role"]
                )

                return redirect("signup_success")

    else:

        form = SignupForm(
            initial={"role": role}
        )

    return render(
        request,
        "accounts/signup.html",
        {
            "form": form,
            "role": role,
        }
    )


# ==========================================
# SIGNUP SUCCESS PAGE
# ==========================================

def signup_success(request):

    role = request.session.get("signup_role")

    if role not in ("customer", "dealer"):
        return redirect("signup")

    return render(
        request,
        "accounts/signup_success.html",
        {
            "role": role
        }
    )


# ==========================================
# DETERMINE USER DASHBOARD
# ==========================================

def dashboard_for(user):

    profile = getattr(user, "profile", None)

    if profile is None:
        return None

    if profile.role == "customer":
        return "customer_dashboard_preview"

    if (
        profile.role == "dealer"
        and profile.dealer_approved
    ):
        return "dealer_dashboard"

    return None


# ==========================================
# REAL LOGIN
# ==========================================

def login_view(request):

    # Already logged in
    if request.user.is_authenticated:

        destination = dashboard_for(request.user)

        if destination:
            return redirect(destination)

    error = None
    email = ""

    if request.method == "POST":

        email = request.POST.get(
            "email", ""
        ).strip().lower()

        password = request.POST.get(
            "password", ""
        )

        if not email or not password:

            error = "Enter your email and password."

        else:

            user = authenticate(
                request,
                username=email,
                password=password
            )

            if user is None:

                error = (
                    "Invalid email/password or "
                    "account awaiting approval."
                )

            else:

                destination = dashboard_for(user)

                if destination:

                    auth_login(request, user)

                    return redirect(destination)

                error = (
                    "This account cannot access "
                    "this login portal."
                )

    return render(
        request,
        "accounts/login.html",
        {
            "email": email,
            "error": error,
        }
    )


# ==========================================
# LOGOUT
# ==========================================

@login_required(login_url="login")
@require_POST
def logout_view(request):

    auth_logout(request)

    return redirect("login")


# ==========================================
# CUSTOMER DASHBOARD
# ==========================================

@login_required(login_url="login")
@never_cache
def customer_dashboard_preview(request):

    if not is_customer(request):
        return HttpResponseForbidden(
            "Customer accounts only."
        )

    submitted = (
        WasteListing.objects
        .filter(customer=request.user)
        .exclude(status="draft")
    )

    draft = get_draft(request.user)

    return render(
        request,
        "customer/dashboard.html",
        {
            "total_listings": submitted.count(),

            "pending_listings": submitted.filter(
                status="pending"
            ).count(),

            "draft_item_count": (
                draft.items.count() if draft else 0
            ),

            "recent_listings": submitted[:3],
        }
    )


# ==========================================
# DEALER DASHBOARD
# ==========================================


@login_required(login_url="login")
@never_cache
def dealer_dashboard(request):

    profile = getattr(request.user, "profile", None)

    if (
        not profile
        or profile.role != "dealer"
        or not profile.dealer_approved
    ):
        return HttpResponseForbidden(
            "Only approved dealers can access this page."
        )

    service_area = profile.service_area.strip()

    # Show available waste only in dealer's area
    if service_area:
        available_listings = (
            WasteListing.objects
            .filter(
                status="pending",
                accepted_by__isnull=True,
                pickup_area__iexact=service_area
            )
            .prefetch_related("items")
            .order_by("-submitted_at")
        )
    else:
        available_listings = WasteListing.objects.none()

    # Listings already accepted by this dealer
    my_pickups = (
        WasteListing.objects
        .filter(
            accepted_by=request.user,
            status="accepted"
        )
        .select_related("customer")
        .prefetch_related("items")
        .order_by("-accepted_at")
    )

    return render(
        request,
        "dealer/dashboard.html",
        {
            "profile": profile,
            "available_listings": available_listings,
            "my_pickups": my_pickups,
        }
    )


# ==========================================
# MY LISTINGS - EMPTY STATE FOR NOW
# ==========================================


@login_required(login_url="login")
@never_cache
def my_listings(request):

    if not is_customer(request):
        return HttpResponseForbidden(
            "Customer accounts only."
        )

    listings = (
        WasteListing.objects
        .filter(customer=request.user)
        .exclude(status="draft")
        .prefetch_related("items")
    )

    return render(
        request,
        "customer/my_listings.html",
        {
            "listings": listings
        }
    )



# ==========================================
# ADD WASTE - STAGE 2 PLACEHOLDER
# ==========================================


@login_required(login_url="login")
@never_cache
def add_waste_preview(request):

    if not is_customer(request):
        return HttpResponseForbidden(
            "Customer accounts only."
        )

    draft = get_draft(request.user)
    edit_item = None

    item_form = WasteItemForm()

    pickup_form = PickupForm(
        initial={
            "pickup_area": (
                draft.pickup_area if draft else ""
            ),
            "pickup_address": (
                draft.pickup_address if draft else ""
            ),
            "pickup_notes": (
                draft.pickup_notes if draft else ""
            ),
        }
    )

    # --------------------------------------
    # EDIT AN EXISTING BASKET ITEM
    # --------------------------------------

    if request.method == "GET":

        item_id = request.GET.get("edit")

        if item_id:

            edit_item = get_object_or_404(
                WasteItem,
                pk=item_id,
                listing__customer=request.user,
                listing__status="draft",
            )

            draft = edit_item.listing

            item_form = WasteItemForm(
                instance=edit_item
            )

    # --------------------------------------
    # HANDLE FORM SUBMISSIONS
    # --------------------------------------

    if request.method == "POST":

        action = request.POST.get("action")

        # ADD / EDIT WASTE ITEM

        if action in ("add_item", "edit_item"):

            if action == "edit_item":

                edit_item = get_object_or_404(
                    WasteItem,
                    pk=request.POST.get("item_id"),
                    listing__customer=request.user,
                    listing__status="draft",
                )

                draft = edit_item.listing

            item_form = WasteItemForm(
                request.POST,
                instance=edit_item
            )

            if item_form.is_valid():

                waste_type = (
                    item_form.cleaned_data["waste_type"]
                )

                rate = WasteRate.objects.filter(
                    waste_type=waste_type,
                    is_active=True
                ).first()

                if rate is None:

                    item_form.add_error(
                        "waste_type",
                        "Price unavailable."
                    )

                else:

                    with transaction.atomic():

                        if draft is None:

                            draft = WasteListing.objects.create(
                                customer=request.user,
                                status="draft"
                            )

                        item = item_form.save(
                            commit=False
                        )

                        item.listing = draft

                        item.category = (
                            WASTE_TYPE_DETAILS[waste_type][0]
                        )

                     
                        # Condition-based price calculation
                        condition_multiplier = CONDITION_RATE_MULTIPLIERS[
                            item.condition
                        ]

                        # Adjust price per kg
                        item.rate_per_kg = (
                            rate.price_per_kg * condition_multiplier
                        ).quantize(Decimal("0.01"))

                        # Calculate estimated amount
                        item.estimated_amount = (
                            item.estimated_weight * item.rate_per_kg
                        ).quantize(Decimal("0.01"))


                        item.save()

                        update_listing_totals(draft)

                    messages.success(
                        request,
                        "Waste item saved to your basket."
                    )

                    return redirect(
                        "add_waste_preview"
                    )

        # REMOVE WASTE ITEM

        elif action == "remove_item":

            item = get_object_or_404(
                WasteItem,
                pk=request.POST.get("item_id"),
                listing__customer=request.user,
                listing__status="draft",
            )

            with transaction.atomic():

                listing = item.listing

                item.delete()

                update_listing_totals(listing)

            messages.success(
                request,
                "Item removed from basket."
            )

            return redirect(
                "add_waste_preview"
            )

        # SUBMIT PICKUP REQUEST

        elif action == "submit_listing":

            pickup_form = PickupForm(
                request.POST
            )

            if (
                draft is None
                or not draft.items.exists()
            ):

                messages.error(
                    request,
                    "Add at least one waste item first."
                )

            elif pickup_form.is_valid():

                with transaction.atomic():

                    update_listing_totals(draft)

                    draft.pickup_area = (
                        pickup_form.cleaned_data[
                            "pickup_area"
                        ]
                    )

                    draft.pickup_address = (
                        pickup_form.cleaned_data[
                            "pickup_address"
                        ]
                    )

                    draft.pickup_notes = (
                        pickup_form.cleaned_data[
                            "pickup_notes"
                        ]
                    )

                    draft.status = "pending"

                    draft.submitted_at = (
                        timezone.now()
                    )

                    draft.save(
                        update_fields=[
                            "pickup_area",
                            "pickup_address",
                            "pickup_notes",
                            "status",
                            "submitted_at",
                        ]
                    )

                messages.success(
                    request,
                    "Pickup request submitted!"
                )

                return redirect(
                    "my_listings"
                )

        else:

            messages.error(
                request,
                "Invalid action."
            )

    # --------------------------------------
    # DISPLAY ORIGINAL HTML DESIGN
    # --------------------------------------

    draft_items = (
        draft.items.all() if draft else []
    )

    rates = (
        WasteRate.objects
        .filter(is_active=True)
        .order_by("waste_type")
    )

    return render(
        request,
        "customer/add_waste.html",
        {
            "item_form": item_form,
            "pickup_form": pickup_form,
            "edit_item": edit_item,
            "draft": draft,
            "draft_items": draft_items,
            "rates": rates,
        }
    )



# ==========================================
# FORGOT PASSWORD - PREVIEW ONLY
# ==========================================

def forgot_password(request):

    if request.method == "POST":
        return redirect("check_email")

    return render(
        request,
        "accounts/forgot_password.html"
    )


def check_email(request):

    return render(
        request,
        "accounts/check_email.html"
    )


def reset_password_preview(request):

    return render(
        request,
        "accounts/reset_password.html",
        {
            "preview_submitted": (
                request.method == "POST"
            )
        }
    )



# ==========================================
# WASTETRADE CUSTOM ADMIN DASHBOARD
# ==========================================

@staff_member_required(login_url="/admin/login/")
@never_cache
def admin_dashboard(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "Only WasteTrade administrators can access this page."
        )

    pending_dealers = (
        UserProfile.objects
        .filter(
            role="dealer",
            dealer_approved=False,
        )
        .select_related("user")
        .order_by("-created_at")
    )

    recent_listings = (
        WasteListing.objects
        .exclude(status="draft")
        .select_related("customer")
        .order_by("-created_at")[:5]
    )

    context = {
        "total_customers": UserProfile.objects.filter(
            role="customer"
        ).count(),

        "total_dealers": UserProfile.objects.filter(
            role="dealer",
            dealer_approved=True,
            user__is_active=True,
        ).count(),

        "pending_dealer_count": pending_dealers.count(),

        "pending_dealers": pending_dealers[:5],

        "total_listings": WasteListing.objects.exclude(
            status="draft"
        ).count(),

        "pending_listings": WasteListing.objects.filter(
            status="pending"
        ).count(),

        "active_rates": WasteRate.objects.filter(
            is_active=True
        ).count(),

        "recent_listings": recent_listings,
    }

    return render(
        request,
        "adminpanel/dashboard.html",
        context
    )

# ==========================================
# DEALER ACCEPTS A WASTE LISTING
# ==========================================

@login_required(login_url="login")
@require_POST
def dealer_accept_listing(request, listing_id):

    profile = getattr(request.user, "profile", None)

    if (
        not profile
        or profile.role != "dealer"
        or not profile.dealer_approved
    ):
        return HttpResponseForbidden(
            "Only approved dealers can accept waste."
        )

    service_area = profile.service_area.strip()

    if not service_area:
        messages.error(
            request,
            "Please set your service area first."
        )
        return redirect("dealer_dashboard")

    # Only one dealer can accept a pending listing.
    # The database update is conditional and atomic.

    updated = (
        WasteListing.objects
        .filter(
            pk=listing_id,
            status="pending",
            accepted_by__isnull=True,
            pickup_area__iexact=service_area
        )
        .update(
            status="accepted",
            accepted_by=request.user,
            accepted_at=timezone.now()
        )
    )

    if updated == 1:
        messages.success(
            request,
            "Waste listing accepted successfully!"
        )
    else:
        messages.error(
            request,
            "Listing unavailable or already accepted."
        )

    return redirect("dealer_dashboard")
