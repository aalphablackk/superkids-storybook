from django.shortcuts import render

# Create your views here.


def home(request):
    """Display the Superkids Storybook homepage."""
    return render(request, "pages/home.html")
