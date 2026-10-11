
from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("books/", views.library, name="library"),
    path("books/<slug:slug>/", views.book_detail, name="book_detail"),
]
