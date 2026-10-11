from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
)
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.urls import reverse
from books.models import ReadingProgress

from .forms import (
    CampaignerApplicationForm,
    ChildProfileForm,
    EmailOrUsernameLoginForm,
    ParentProfileForm,
    ParentRegistrationForm,
)
from .models import (
    CampaignerProfile,
    ChildProfile,
    ParentProfile,
    User,
)

# Create your views here.

def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = ParentRegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                ParentProfile.objects.create(user=user)

            login(request, user)
            messages.success(
                request,
                "Your account has been created successfully.",
            )
            return redirect("accounts:dashboard")
    else:
        form = ParentRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailOrUsernameLoginForm
    redirect_authenticated_user = True


@login_required
@require_POST
def account_logout(request):
    logout(request)
    messages.success(request, "You have signed out successfully.")
    return redirect("books:home")


class AccountPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


def password_reset_done(request):
    return render(request, "accounts/password_reset_done.html")


def password_reset_confirm(request, uidb64, token):
    from django.contrib.auth.views import PasswordResetConfirmView

    view = PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url=reverse_lazy("accounts:password_reset_complete"),
    )
    return view(request, uidb64=uidb64, token=token)


def password_reset_complete(request):
    return render(request, "accounts/password_reset_complete.html")


@login_required
def dashboard(request):
    children = request.user.children.all()

    recent_progress = (
        ReadingProgress.objects.filter(child__parent=request.user)
        .select_related("child", "book", "book__author")
        .order_by("-last_read_at")[:6]
    )

    parent_profile, _ = ParentProfile.objects.get_or_create(
        user=request.user
    )

    campaigner_profile = getattr(
        request.user,
        "campaigner_profile",
        None,
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "children": children,
            "recent_progress": recent_progress,
            "parent_profile": parent_profile,
            "campaigner_profile": campaigner_profile,
        },
    )


@login_required
def parent_profile(request):
    profile, _ = ParentProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ParentProfileForm(request.POST,request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your profile has been updated.",
            )
            return redirect("accounts:profile")
    else:
        form = ParentProfileForm(instance=profile)

    return render(
        request,
        "accounts/profile.html",
        {"form": form},
    )


# @login_required
# def child_list(request):
#     children = request.user.children.all()

#     return render(
#         request,
#         "accounts/children/list.html",
#         {"children": children},
        
#     )
@login_required
def child_list(request):
    children = ChildProfile.objects.filter(
        parent=request.user
    ).order_by("first_name", "last_name")

    return render(
        request,
        "accounts/children.html",
        {
            "children": children,
            "child_create_url": reverse("accounts:child_create"),
        },
    )


@login_required
def child_create(request):
    if request.method == "POST":
        form = ChildProfileForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            messages.success(request, "Child profile added successfully.")
            return redirect("accounts:child_detail", pk=child.pk)
    else:
        form = ChildProfileForm()

    return render(request, "accounts/child_form.html", {
        "form": form,
        "child": None,
        "page_title": "Add a child profile",
    })


@login_required
def child_edit(request, pk):
    child = get_object_or_404(
        ChildProfile,
        pk=pk,
        parent=request.user,
    )

    if request.method == "POST":
        form = ChildProfileForm(
            request.POST,
            request.FILES,
            instance=child,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Child profile updated successfully.")
            return redirect("accounts:child_detail", pk=child.pk)
    else:
        form = ChildProfileForm(instance=child)

    return render(request, "accounts/child_form.html", {
        "form": form,
        "child": child,
        "page_title": "Edit child profile",
    })



@login_required
def child_detail(request, pk):
    child = get_object_or_404(
        ChildProfile,
        pk=pk,
        parent=request.user,
    )

    reading_progress = (
        ReadingProgress.objects
        .filter(child=child)
        .select_related("book")
        .order_by("-last_read_at")
    )

    context = {
        "child": child,
        "reading_progress": reading_progress,
        "library_url": reverse("books:library"),
        "delete_url": reverse(
            "accounts:child_delete",
            kwargs={"pk": child.pk},
        ),
    }

    return render(
        request,
        "accounts/child_detail.html",
        context,
    )



@login_required
@require_POST
def child_delete(request, pk):
    child = get_object_or_404(
        ChildProfile,
        pk=pk,
        parent=request.user,
    )
    child_name = child.first_name
    child.delete()
    

    messages.success(
        request,
        f"{child_name}'s profile has been deleted.",
    )
    return redirect("accounts:children"
                    )


@login_required
def campaigner_apply(request):
    existing = getattr(
        request.user,
        "campaigner_profile",
        None,
    )

    if existing:
        messages.info(
            request,
            "You already have a campaigner application.",
        )
        return redirect("accounts:campaigner_dashboard")

    if request.method == "POST":
        form = CampaignerApplicationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()

                request.user.role = User.Role.CAMPAIGNER
                request.user.save(update_fields=["role"])

            messages.success(
                request,
                "Your campaigner application has been submitted "
                "for review.",
            )
            return redirect("accounts:campaigner_dashboard")
    else:
        form = CampaignerApplicationForm()

    return render(
        request,
        "accounts/campaigner_apply.html",
        {"form": form},
    )


@login_required
def campaigner_dashboard(request):
    profile = get_object_or_404(
        CampaignerProfile,
        user=request.user,
    )

    return render(
        request,
        "accounts/campaigner_dashboard.html",
        {"profile": profile},
    )
