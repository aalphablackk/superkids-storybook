
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    CampaignerProfile,
    ChildProfile,
    ParentProfile,
    User,
)
from datetime import date
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import get_child_age


class BootstrapFormMixin:
    """Apply consistent Bootstrap styling to form fields."""

    def apply_bootstrap(self):
        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"

            existing_class = widget.attrs.get("class", "")
            classes = existing_class.split()

            if css_class not in classes:
                classes.append(css_class)

            widget.attrs["class"] = " ".join(classes)


class ParentRegistrationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "family-name"}),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

        self.fields["username"].help_text = (
            "Choose a username you can easily remember."
        )
        self.fields["password1"].help_text = (
            "Use a strong password that you have not used elsewhere."
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip()
        user.role = User.Role.PARENT

        if commit:
            user.save()

        return user


class ParentProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = (
            "profile_image",
            "phone",
            "whatsapp_number",
            "social_media",
            "occupation",
            "home_address",
            "office_address",
        )
        widgets = {
            "home_address": forms.Textarea(attrs={"rows": 3}),
            "office_address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class ChildProfileForm(BootstrapFormMixin, forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = ChildProfile
        fields = (
            "profile_image",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "school",
            "class_level",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.localdate()
        min_age = settings.SUPERKIDS_MIN_AGE
        target_year = today.year - min_age

        # Handle leap years safely.
        import calendar
        max_day = min(today.day, calendar.monthrange(
            target_year, today.month
        )[1])

        latest_dob = date(target_year, today.month, max_day)

        self.fields["date_of_birth"].widget.attrs["max"] = (
            latest_dob.isoformat()
        )

    def clean_date_of_birth(self):
        dob = self.cleaned_data["date_of_birth"]

        if get_child_age(dob) < settings.SUPERKIDS_MIN_AGE:
            raise ValidationError(
                f"Children must be at least "
                f"{settings.SUPERKIDS_MIN_AGE} years old to register."
            )

        return dob

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class CampaignerApplicationForm(
    BootstrapFormMixin,
    forms.ModelForm,
):
    class Meta:
        model = CampaignerProfile
        fields = (
            "occupation",
            "workplace",
            "phone",
            "whatsapp_number",
            "address",
            "social_media",
            "course_of_study",
            "tertiary_institution",
            "has_children_ngo_experience",
            "ngo_name",
            "ngo_address",
            "ngo_assignment",
            "motivation",
            "promotion_plan",
            "target_schools",
            "target_students",
            "preferred_school_visit_time",
        )
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "ngo_address": forms.Textarea(attrs={"rows": 3}),
            "ngo_assignment": forms.Textarea(attrs={"rows": 3}),
            "motivation": forms.Textarea(attrs={"rows": 4}),
            "promotion_plan": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

class EmailOrUsernameLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or email",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your username or email",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )
