
from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from decimal import Decimal
from .models import WasteItem, WasteRate
from django.utils import timezone
User = get_user_model()


class SignupForm(forms.Form):

    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("dealer", "Dealer"),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.HiddenInput()
    )

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter your full name",
            "autocomplete": "name",
        })
    )

    phone = forms.RegexField(
        regex=r"^[6-9][0-9]{9}$",
        max_length=10,
        error_messages={
            "invalid": "Enter a valid 10-digit mobile number."
        },
        widget=forms.TextInput(attrs={
            "placeholder": "10-digit mobile number",
            "inputmode": "numeric",
            "maxlength": "10",
        })
    )

    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email",
            "autocomplete": "email",
        })
    )

    shop_name = forms.CharField(
        max_length=150,
        required=False
    )

    service_area = forms.CharField(
        max_length=150,
        required=False
    )

    password1 = forms.CharField(
        min_length=8,
        max_length=128,
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
        })
    )

    password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
        })
    )

    # Check duplicate email
    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            Q(username__iexact=email) |
            Q(email__iexact=email)
        ).exists():

            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    # Validate form
    def clean(self):

        data = super().clean()

        role = data.get("role")

        if role == "dealer":

            if not data.get("shop_name", "").strip():
                self.add_error(
                    "shop_name",
                    "Shop name is required for dealers."
                )

            if not data.get("service_area", "").strip():
                self.add_error(
                    "service_area",
                    "Service area is required for dealers."
                )

        elif role == "customer":

            data["shop_name"] = ""
            data["service_area"] = ""

        password1 = data.get("password1")
        password2 = data.get("password2")

        if password1 and password2:

            if password1 != password2:
                self.add_error(
                    "password2",
                    "Passwords do not match."
                )

        return data



# ==========================================
# ADD WASTE ITEM FORM
# ==========================================

class WasteItemForm(forms.ModelForm):

    class Meta:
        model = WasteItem

        fields = [
            "waste_type",
            "estimated_weight",
            "condition",
        ]

        labels = {
            "waste_type": "Waste Category and Type",
            "estimated_weight": "Estimated Weight (kg)",
            "condition": "Waste Condition",
        }

        widgets = {
            "waste_type": forms.Select(
                attrs={"class": "input"}
            ),

            "estimated_weight": forms.NumberInput(
                attrs={
                    "class": "input",
                    "min": "0.10",
                    "step": "0.01",
                    "placeholder": "Example: 5",
                }
            ),

            "condition": forms.Select(
                attrs={"class": "input"}
            ),
        }

    def clean_waste_type(self):

        waste_type = self.cleaned_data["waste_type"]

        if not WasteRate.objects.filter(
            waste_type=waste_type,
            is_active=True
        ).exists():

            raise forms.ValidationError(
                "Price unavailable for this waste type."
            )

        return waste_type

    def clean_estimated_weight(self):

        weight = self.cleaned_data["estimated_weight"]

        if (
            weight < Decimal("0.10")
            or weight > Decimal("10000.00")
        ):
            raise forms.ValidationError(
                "Enter a weight between 0.10 and 10000 kg."
            )

        return weight


# ==========================================
# PICKUP DETAILS FORM
# ==========================================

class PickupForm(forms.Form):

    pickup_area = forms.CharField(
        max_length=120,
        label="Pickup Area / City",
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Example: Alappuzha",
            }
        )
    )

    pickup_address = forms.CharField(
        min_length=10,
        max_length=500,
        label="Pickup Address",
        widget=forms.Textarea(
            attrs={
                "class": "input",
                "rows": 3,
                "placeholder": (
                    "House name, street, landmark, PIN code"
                ),
            }
        )
    )

    pickup_notes = forms.CharField(
        required=False,
        max_length=300,
        label="Pickup Instructions (Optional)",
        widget=forms.Textarea(
            attrs={
                "class": "input",
                "rows": 2,
                "placeholder": "Any special instructions",
            }
        )
    )

# ==========================================
# DEALER PICKUP SCHEDULING FORM
# ==========================================

class PickupScheduleForm(forms.Form):

    pickup_scheduled_at = forms.DateTimeField(
        label="Pickup Date and Time",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "required": True,
            }
        )
    )

    def clean_pickup_scheduled_at(self):

        pickup_datetime = self.cleaned_data[
            "pickup_scheduled_at"
        ]

        if pickup_datetime <= timezone.now():
            raise forms.ValidationError(
                "Please select a future pickup date and time."
            )

        return pickup_datetime
