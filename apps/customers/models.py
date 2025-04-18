from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import BaseModel


# Create your models here.
class Customer(BaseModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("prospect", "Prospect"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def get_absolute_url(self):
        return reverse("customer-detail", args=[str(self.id)])

    @property
    def get_customer_details(self):
        return f"{self.name} - {self.company} - ({self.get_status_display()})"

    @property
    def last_interactions(self):
        return self.interactions.order_by("-interaction_date").first()

    @property
    def total_interactions(self):
        return self.interactions_set.count()

    @property
    def days_since_last_interaction(self):
        if self.last_interactions:
            return (timezone.now() - self.last_interactions.interaction_date).days
        return None
