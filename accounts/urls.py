
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", views.account_logout, name="logout"),

    path("password-reset/", views.AccountPasswordResetView.as_view(),
         name="password_reset"),
    path("password-reset/done/", views.password_reset_done,
         name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/",
         views.password_reset_confirm, name="password_reset_confirm"),
    path("password-reset/complete/", views.password_reset_complete,
         name="password_reset_complete"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.parent_profile, name="profile"),

    path("children/", views.child_list, name="children"),
    path("children/add/", views.child_create, name="child_create"),
    path("children/<int:pk>/", views.child_detail, name="child_detail"),
    path("children/<int:pk>/edit/", views.child_edit, name="child_edit"),
    path("children/<int:pk>/delete/", views.child_delete,
         name="child_delete"),

    path("campaigner/apply/", views.campaigner_apply,
         name="campaigner_apply"),
    path("campaigner/dashboard/", views.campaigner_dashboard,
         name="campaigner_dashboard"),
]
