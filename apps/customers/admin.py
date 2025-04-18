from django.contrib import admin

from .models import Customer


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "status",
        "company",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "company")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {"fields": ("name", "email", "phone", "status")}),
        ("Company Information", {"fields": ("company", "notes")}),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
