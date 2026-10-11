from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from accounts.models import ChildProfile
from .models import Book, Category, ReadingProgress


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
    """Display a storybook and its online reading content."""
    book = get_object_or_404(
        Book.objects.select_related("author", "category"),
        slug=slug,
        is_active=True,
        category__is_active=True,
    )

    children = ChildProfile.objects.none()
    selected_child = None
    reading_progress = None

    if request.user.is_authenticated:
        children = ChildProfile.objects.filter(
            parent=request.user
        ).order_by("first_name", "last_name")

        child_id = request.GET.get("child")

        if child_id:
            selected_child = children.filter(pk=child_id).first()

            if selected_child:
                reading_progress = ReadingProgress.objects.filter(
                    child=selected_child,
                    book=book,
                ).first()

    context = {
        "book": book,
        "children": children,
        "selected_child": selected_child,
        "reading_progress": reading_progress,
    }

    return render(request, "pages/book_detail.html", context)
