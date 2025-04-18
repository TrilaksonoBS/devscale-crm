from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.customers.models import Customer
from apps.interactions.models import Interaction
from core.views import LoginRequiredMixinView


class DashboardView(LoginRequiredMixinView, TemplateView):
    template_name = "dashboard.html"
    context_object_name = "dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        # statistics
        total_customers = Customer.objects.count()
        active_customers = Customer.objects.filter(status="active").count()

        # distribution
        status_distribution = []
        for value, label in Customer.STATUS_CHOICES:
            count = Customer.objects.filter(status=value).count()
            status_distribution.append({"status": label, "count": count})

        # Recent interactions - include time in the filtering
        recent_interactions = (
            Interaction.objects.filter(
                interaction_date__gte=timezone.make_aware(
                    datetime.combine(week_ago, datetime.min.time())
                ),
                interaction_date__lte=timezone.make_aware(
                    datetime.combine(today, datetime.max.time())
                ),
            )
            .select_related("customer")
            .order_by("-interaction_date")[:5]
        )

        # upcoming follow-ups - include time in the filtering
        next_week = today + timedelta(days=7)
        upcoming_followups = Interaction.objects.filter(
            follow_up_date__gte=timezone.make_aware(
                datetime.combine(today, datetime.min.time())
            ),
            follow_up_date__lte=timezone.make_aware(
                datetime.combine(next_week, datetime.max.time())
            ),
        ).count()

        # follow-up list
        upcoming_followups_list = (
            Interaction.objects.filter(
                follow_up_date__gte=timezone.make_aware(
                    datetime.combine(today, datetime.min.time())
                ),
                follow_up_date__lte=timezone.make_aware(
                    datetime.combine(next_week, datetime.max.time())
                ),
            )
            .select_related("customer")
            .order_by("follow_up_date")
        )

        context.update(
            {
                "total_customers": total_customers,
                "active_customers": active_customers,
                "status_distribution": status_distribution,
                "recent_interactions": recent_interactions,
                "recent_interactions_list": recent_interactions,
                "upcoming_followups": upcoming_followups,
                "upcoming_followups_list": upcoming_followups_list,
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class CustomerListView(LoginRequiredMixinView, ListView):
    model = Customer
    template_name = "customers/customer_list.html"
    context_object_name = "customers"
    paginate_by = 10

    def get_queryset(self):
        queryset = Customer.objects.all()
        search_query = self.request.GET.get("q")
        status_filter = self.request.GET.get("status")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(company__icontains=search_query)
            )

        if status_filter and status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        return queryset.annotate(interactions_count=Count("interactions"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Customer.STATUS_CHOICES
        context["current_status"] = self.request.GET.get("status", "all")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class CustomerDetailView(LoginRequiredMixinView, DetailView):
    model = Customer
    template_name = "customers/customer_detail.html"
    context_object_name = "customer"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interactions"] = Interaction.objects.filter(
            customer=self.object
        ).order_by("-interaction_date")
        return context


class CustomerCreateView(LoginRequiredMixinView, CreateView):
    model = Customer
    template_name = "customers/customer_form.html"
    fields = ["name", "email", "phone", "status", "company", "notes"]
    success_url = reverse_lazy("customer-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Customer"
        context["button_text"] = "Create Customer"
        return context


class CustomerUpdateView(LoginRequiredMixinView, UpdateView):
    model = Customer
    template_name = "customers/customer_form.html"
    fields = ["name", "email", "phone", "status", "company", "notes"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Update {self.object.name}"
        context["button_text"] = "Update Customer"
        return context

    def get_success_url(self):
        return reverse_lazy("customer-detail", kwargs={"pk": self.object.pk})


class CustomerDeleteView(LoginRequiredMixinView, DeleteView):
    model = Customer
    template_name = "customers/customer_confirmation.html"
    success_url = reverse_lazy("customer-list")
    context_object_name = "customer"


class InteractionListView(LoginRequiredMixinView, ListView):
    model = Interaction
    template_name = "interactions/interaction_list.html"
    context_object_name = "interactions"
    paginate_by = 15

    def get_queryset(self):
        queryset = Interaction.objects.all().select_related("customer", "created_by")

        customer_id = self.request.GET.get("customer")
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        interaction_type = self.request.GET.get("type")
        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)

        from core.utils import get_date_range_from_request

        start_date, end_date = get_date_range_from_request(self.request)

        queryset = queryset.filter(
            interaction_date__date__gte=start_date, interaction_date__date__lte=end_date
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interaction_types"] = Interaction.INTERACTION_TYPE_CHOICES
        context["customers"] = Customer.objects.all()
        context["selected_customer"] = self.request.GET.get("customer", "")
        context["selected_type"] = self.request.GET.get("type", "")

        from core.utils import get_date_range_from_request

        start_date, end_date = get_date_range_from_request(self.request)
        context["start_date"] = start_date.strftime("%Y-%m-%d")
        context["end_date"] = end_date.strftime("%Y-%m-%d")

        return context


class InteractionDetailView(LoginRequiredMixinView, DetailView):
    model = Interaction
    template_name = "interactions/interaction_detail.html"
    context_object_name = "interaction"


class InteractionCreateView(LoginRequiredMixinView, CreateView):
    model = Interaction
    template_name = "interactions/interaction_form.html"
    fields = [
        "customer",
        "interaction_type",
        "interaction_date",
        "summary",
        "follow_up_date",
    ]

    def get_initial(self):
        initial = super().get_initial()
        customer_id = self.kwargs.get("pk")
        if customer_id:
            initial["customer"] = get_object_or_404(Customer, pk=customer_id)
        initial["interaction_date"] = timezone.now()
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        # Ensure follow_up_date is timezone aware
        if form.instance.follow_up_date and timezone.is_naive(
            form.instance.follow_up_date
        ):
            form.instance.follow_up_date = timezone.make_aware(
                form.instance.follow_up_date
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_id = self.kwargs.get("pk")
        if customer_id:
            context["customer"] = get_object_or_404(Customer, pk=customer_id)
            context["title"] = f"Add Interaction for {context['customer'].name}"
        else:
            context["title"] = "Add New Interaction"
        context["button_text"] = "Create Interaction"
        return context

    def get_success_url(self):
        customer_id = self.kwargs.get("pk")
        if customer_id:
            return reverse_lazy("customer-detail", kwargs={"id": customer_id})
        else:
            return reverse_lazy("interaction-list")


class InteractionUpdateView(LoginRequiredMixinView, UpdateView):
    model = Interaction
    template_name = "interactions/interaction_form.html"
    fields = [
        "customer",
        "interaction_type",
        "interaction_date",
        "summary",
        "follow_up_date",
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Update Interaction for {self.object.customer.name}"
        context["button_text"] = "Update Interaction"
        return context

    def get_success_url(self):
        return reverse_lazy("interaction-detail", kwargs={"pk": self.object.pk})


class InteractionDeleteView(LoginRequiredMixinView, DeleteView):
    model = Interaction
    template_name = "interactions/interaction_confirmation.html"
    context_object_name = "interaction"

    def get_success_url(self):
        if self.object.customer:
            return reverse_lazy(
                "customer-detail", kwargs={"id": self.object.customer.id}
            )
        return reverse_lazy("interaction-list")


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("login")
