from django.contrib import admin

from .models import Interaction

# Register your models here.


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "interaction_type",
        "interaction_date",
        "summary",
        "follow_up_date",
        "reminder_set",
        "created_by",
    )
    list_filter = ("interaction_type", "interaction_date", "customer", "reminder_set")
    search_fields = ("customer__name", "summary")
    ordering = ("-interaction_date",)
    readonly_fields = ("created_at", "updated_at", "reminder_set", "interaction_date")

    fieldsets = (
        ("Customer Information", {"fields": ("customer",)}),
        (
            "Interaction Details",
            {"fields": ("interaction_type", "interaction_date", "summary")},
        ),
        ("Follow-up", {"fields": ("follow_up_date", "reminder_set")}),
        (
            "System Information",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj._current_user = request.user
        super().save_model(request, obj, form, change)
