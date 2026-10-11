
from datetime import date

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def get_child_age(date_of_birth, today=None):
    """Calculate age accurately, accounting for birthdays."""
    if not date_of_birth:
        return None

    today = today or timezone.localdate()

    return (
        today.year
        - date_of_birth.year
        - (
            (today.month, today.day)
            < (date_of_birth.month, date_of_birth.day)
        )
    )


def is_eligible_for_club(date_of_birth, today=None):
    """Return whether a child meets the configured age limits."""
    age = get_child_age(date_of_birth, today)

    return (
        age is not None
        and settings.SUPERKIDS_MIN_AGE
        <= age
        <= settings.SUPERKIDS_MAX_AGE
    )


class User(AbstractUser):
    class Role(models.TextChoices):
        PARENT = "PARENT", "Parent / Guardian"
        CAMPAIGNER = "CAMPAIGNER", "Campaigner"

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARENT,
    )

    def __str__(self):
        return self.get_full_name() or self.username


class ParentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parent_profile",
    )
    profile_image = models.ImageField(
        upload_to="profiles/parents/",
        blank=True,
        null=True,
    )

    phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    social_media = models.CharField(max_length=255, blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    home_address = models.TextField(blank=True)
    office_address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parent profile: {self.user}"


class ChildProfile(models.Model):
    class Gender(models.TextChoices):
        GIRL = "GIRL", "Girl"
        BOY = "BOY", "Boy"
        OTHER = "OTHER", "Other"
        NOT_SPECIFIED = "NOT_SPECIFIED", "Prefer not to say"

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children",
    )
    profile_image = models.ImageField(
        upload_to="profiles/children/",
        blank=True,
        null=True,
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)

    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
    )

    school = models.CharField(max_length=200, blank=True)
    class_level = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        return get_child_age(self.date_of_birth)

    @property
    def is_eligible_for_club(self):
        return is_eligible_for_club(self.date_of_birth)

    
    def clean(self):
        super().clean()

        if self.date_of_birth:
            today = timezone.localdate()

            if self.date_of_birth > today:
                raise ValidationError({
                    "date_of_birth": "Date of birth cannot be in the future."
                })

            if get_child_age(self.date_of_birth, today) < settings.SUPERKIDS_MIN_AGE:
                raise ValidationError({
                    "date_of_birth": (
                        f"Children must be at least "
                        f"{settings.SUPERKIDS_MIN_AGE} years old to register."
                    )
                })


    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class CampaignerProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigner_profile",
    )
    profile_image = models.ImageField(
        upload_to="profiles/campaigners/",
        blank=True,
        null=True,
    )

    occupation = models.CharField(max_length=150, blank=True)
    workplace = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    social_media = models.CharField(max_length=255, blank=True)

    course_of_study = models.CharField(max_length=200, blank=True)
    tertiary_institution = models.CharField(max_length=200, blank=True)

    has_children_ngo_experience = models.BooleanField(default=False)
    ngo_name = models.CharField(max_length=200, blank=True)
    ngo_address = models.TextField(blank=True)
    ngo_assignment = models.TextField(blank=True)

    motivation = models.TextField(blank=True)
    promotion_plan = models.TextField(blank=True)

    target_schools = models.PositiveIntegerField(null=True, blank=True)
    target_students = models.PositiveIntegerField(null=True, blank=True)
    preferred_school_visit_time = models.CharField(
        max_length=200,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Campaigner: {self.user}"
