from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
    )
    image_url = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def clean(self):
        super().clean()

        if self.image and self.image_url:
            raise ValidationError(
                "Use either an uploaded category image or an image URL, not both."
            )

    @property
    def image_source(self):
        if self.image:
            return self.image.url
        return self.image_url or None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    biography = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to="authors/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="books",
    )

    description = models.TextField(
        help_text="A short introduction displayed in the library."
    )
    story_content = models.TextField(
        blank=True,
        help_text=(
            "The story text displayed on the online reading page. "
            "Leave blank if the story has not been added yet."
        ),
    )

    isbn = models.CharField(
        max_length=13,
        unique=True,
        blank=True,
        null=True,
    )

    age_min = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(18)],
    )
    age_max = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(18)],
    )

    publisher = models.CharField(max_length=200, blank=True)
    pages = models.PositiveIntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default="English")

    poster = models.ImageField(
        upload_to="books/posters/",
        blank=True,
        null=True,
    )
    poster_url = models.URLField(blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["is_featured", "is_active"]),
        ]

    def clean(self):
        super().clean()

        if self.poster and self.poster_url:
            raise ValidationError(
                "Use either an uploaded book cover or a cover URL, not both."
            )

        if (
            self.age_min is not None
            and self.age_max is not None
            and self.age_min > self.age_max
        ):
            raise ValidationError(
                "Minimum reading age cannot exceed maximum reading age."
            )

    @property
    def poster_source(self):
        if self.poster:
            return self.poster.url
        return self.poster_url or None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ReadingProgress(models.Model):
    child = models.ForeignKey(
        "accounts.ChildProfile",
        on_delete=models.CASCADE,
        related_name="reading_progress",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reading_progress",
    )
    current_page = models.PositiveIntegerField(default=1)
    is_completed = models.BooleanField(default=False)
    last_read_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_read_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["child", "book"],
                name="unique_child_book_reading_progress",
            )
        ]

    def __str__(self):
        return f"{self.child} — {self.book.title}"
    
