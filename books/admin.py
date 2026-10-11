from django.contrib import admin

from .models import Author, Book, Category
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "biography")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "is_featured",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "author", "is_featured", "is_active")
    search_fields = (
        "title",
        "author__name",
        "category__name",
        "isbn",
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Book Details",
            {
                "fields": (
                    "title",
                    "slug",
                    "author",
                    "category",
                    "description",
                    "story_content",
                    "isbn",
                )
            },
        ),
        (
            "Reading Information",
            {
                "fields": (
                    "age_min",
                    "age_max",
                    "language",
                    "publisher",
                    "pages",
                )
            },
        ),
        (
            "Book Cover",
            {
                "fields": ("poster", "poster_url"),
            },
        ),
        (
            "Publication Status",
            {
                "fields": ("is_featured", "is_active"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
