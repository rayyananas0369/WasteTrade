
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("dealer", "Dealer"),
        ("collector", "Collector"),
        ("admin", "Admin"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer"
    )

    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[6-9][0-9]{9}$",
                message="Enter a valid 10-digit phone number."
            )
        ]
    )

    shop_name = models.CharField(
        max_length=150,
        blank=True
    )

    service_area = models.CharField(
        max_length=150,
        blank=True
    )

    dealer_approved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"



# ==========================================
# WASTE CATEGORIES AND TYPES
# ==========================================

WASTE_TYPE_DETAILS = {
    "newspapers": ("paper", "Old Newspapers"),
    "cardboard": ("paper", "Cardboard"),
    "books": ("paper", "Old Books"),

    "plastic_bottles": ("plastic", "Plastic Bottles"),
    "hard_plastic": ("plastic", "Hard Plastic"),
    "mixed_plastic": ("plastic", "Mixed Plastic"),

    "iron": ("metal", "Iron"),
    "aluminium": ("metal", "Aluminium"),
    "steel": ("metal", "Steel"),

    "electronics": ("ewaste", "Old Electronics"),
    "wires": ("ewaste", "Wires"),
    "circuit_boards": ("ewaste", "Circuit Boards"),
}

CATEGORY_LABELS = {
    "paper": "Paper",
    "plastic": "Plastic",
    "metal": "Metal",
    "ewaste": "E-Waste",
}

WASTE_TYPE_CHOICES = [
    (
        waste_type,
        f"{CATEGORY_LABELS[category]} — {label}"
    )
    for waste_type, (category, label)
    in WASTE_TYPE_DETAILS.items()
]


# ==========================================
# ADMIN-MANAGED WASTE RATES
# ==========================================

class WasteRate(models.Model):

    waste_type = models.CharField(
        max_length=40,
        choices=WASTE_TYPE_CHOICES,
        unique=True
    )

    price_per_kg = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return (
            f"{self.get_waste_type_display()} "
            f"- Rs. {self.price_per_kg}/kg"
        )


# ==========================================
# CUSTOMER WASTE LISTINGS
# ==========================================

class WasteListing(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft Basket"),
        ("pending", "Pending Dealer"),
        ("accepted", "Accepted"),
        ("picked_up", "Picked Up"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="waste_listings"
    )


    # Dealer who accepted the waste listing
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_waste_listings"
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    pickup_scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )


    pickup_area = models.CharField(
        max_length=120,
        blank=True
    )

    pickup_address = models.TextField(
        blank=True
    )

    pickup_notes = models.CharField(
        max_length=300,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True
    )

    estimated_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    estimated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Listing #{self.pk} - {self.status}"


# ==========================================
# INDIVIDUAL WASTE ITEMS
# ==========================================

class WasteItem(models.Model):

    CONDITION_CHOICES = [
        ("clean_dry", "Clean / Dry"),
        ("mixed", "Mixed"),
        ("damaged", "Damaged / Used"),
    ]

    listing = models.ForeignKey(
        WasteListing,
        on_delete=models.CASCADE,
        related_name="items"
    )

    category = models.CharField(
        max_length=20
    )

    waste_type = models.CharField(
        max_length=40,
        choices=WASTE_TYPE_CHOICES
    )

    estimated_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.10"))
        ]
    )

    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES
    )

    rate_per_kg = models.DecimalField(
        max_digits=9,
        decimal_places=2
    )

    estimated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.get_waste_type_display()} "
            f"- {self.estimated_weight} kg"
        )
