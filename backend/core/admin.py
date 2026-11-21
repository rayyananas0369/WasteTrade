
from django.contrib import admin
from django.db import transaction

from .models import UserProfile, WasteRate, WasteListing


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
        "phone",
        "dealer_approved",
        "is_active",
    )

    list_filter = (
        "role",
        "dealer_approved",
    )

    search_fields = (
        "user__username",
        "user__email",
        "shop_name",
        "phone",
    )

    readonly_fields = (
        "created_at",
    )

    actions = [
        "approve_dealers",
    ]

    @admin.display(
        boolean=True,
        description="Active"
    )
    def is_active(self, obj):
        return obj.user.is_active

    @admin.action(
        description="Approve selected dealers"
    )
    def approve_dealers(self, request, queryset):

        count = 0

        with transaction.atomic():

            dealers = queryset.filter(
                role="dealer",
                dealer_approved=False
            ).select_related("user")

            for profile in dealers:

                profile.dealer_approved = True

                profile.save(
                    update_fields=["dealer_approved"]
                )

                profile.user.is_active = True

                profile.user.save(
                    update_fields=["is_active"]
                )

                count += 1

        self.message_user(
            request,
            f"Approved {count} dealer account(s)."
        )


@admin.register(WasteRate)
class WasteRateAdmin(admin.ModelAdmin):

    list_display = (
        "waste_type",
        "price_per_kg",
        "is_active",
    )

    list_filter = ("is_active",)

    list_editable = (
        "price_per_kg",
        "is_active",
    )


# Waste requests in Django administration

@admin.register(WasteListing)
class WasteListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "pickup_area",
        "status",
        "estimated_weight",
        "estimated_amount",
        "submitted_at",
    )

    list_filter = ("status",)

    search_fields = (
        "customer__username",
        "pickup_area",
    )

    def has_add_permission(self, request):
        return False


# Branding for built-in Django Admin

admin.site.site_header = "WasteTrade Management"
admin.site.site_title = "WasteTrade Admin"
admin.site.index_title = "Platform Administration"
