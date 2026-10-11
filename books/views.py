from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Book, Category

# Create your views here.

def home(request):
    """Display the Superkids Storybook homepage."""
    featured_books = (
        Book.objects.filter(
            is_active=True,
            is_featured=True,
            category__is_active=True,
        )
        .select_related("author", "category")[:6]
    )

    return render(
        request,
        "pages/home.html",
        {"featured_books": featured_books},
    )


def about(request):
    """Display the Superkids Storybook About page."""
    return render(request, "pages/about.html")


def library(request):
    """Display the public, free storybook library."""
    books = (
        Book.objects.filter(
            is_active=True,
            category__is_active=True,
        )
        .select_related("author", "category")
    )

    search_query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(author__name__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    if selected_category:
        books = books.filter(category__slug=selected_category)

    categories = Category.objects.filter(is_active=True)

    paginator = Paginator(books, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "books": page_obj.object_list,
        "categories": categories,
        "search_query": search_query,
        "selected_category": selected_category,
    }

    return render(request, "pages/library.html", context)


def book_detail(request, slug):
    """Display an individual storybook and its online reading content."""
    book = get_object_or_404(
        Book.objects.select_related("author", "category"),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )

    return render(
        request,
        "pages/book_detail.html",
        {"book": book},
    )
