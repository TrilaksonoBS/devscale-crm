from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("customers/", views.CustomerListView.as_view(), name="customer-list"),
    path(
        "customers/create/", views.CustomerCreateView.as_view(), name="customer-create"
    ),
    path(
        "customers/<str:id>/",
        views.CustomerDetailView.as_view(),
        name="customer-detail",
    ),
    path(
        "customers/<str:pk>/update/",
        views.CustomerUpdateView.as_view(),
        name="customer-update",
    ),
    path(
        "customers/<str:pk>/delete/",
        views.CustomerDeleteView.as_view(),
        name="customer-delete",
    ),
    # Interaction routes
    path("interactions/", views.InteractionListView.as_view(), name="interaction-list"),
    path(
        "interactions/create/",
        views.InteractionCreateView.as_view(),
        name="interaction-create",
    ),
    path(
        "interactions/create/customer/<str:pk>/",
        views.InteractionCreateView.as_view(),
        name="interaction-create-for-customer",
    ),
    path(
        "interactions/<str:pk>/",
        views.InteractionDetailView.as_view(),
        name="interaction-detail",
    ),
    path(
        "interactions/<str:pk>/update/",
        views.InteractionUpdateView.as_view(),
        name="interaction-update",
    ),
    path(
        "interactions/<str:pk>/delete/",
        views.InteractionDeleteView.as_view(),
        name="interaction-delete",
    ),
]
