from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import BaseModel


# Create your models here.
class Interaction(BaseModel):
    INTERACTION_TYPE_CHOICES = [
        ("call", "Call"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("note", "Note"),
        ("other", "Other"),
    ]

    customer = models.ForeignKey(
        "customers.Customer",
        related_name="interactions",
        on_delete=models.CASCADE,
    )
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPE_CHOICES)
    interaction_date = models.DateTimeField(default=timezone.now)
    summary = models.TextField()
    follow_up_date = models.DateTimeField(blank=True, null=True)
    reminder_set = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "auth.User",
        related_name="interactions_created",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-interaction_date"]
        verbose_name = "Interaction"
        verbose_name_plural = "Interactions"

    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.customer.name} on {self.interaction_date.strftime('%Y-%m-%d')}"

    def get_absolute_url(self):
        return reverse("interaction-detail", kwargs={"id": str(self.id)})

    def save(self, *args, **kwargs):
        if not self.created_by_id and hasattr(self, "_current_user"):
            self.created_by = self._current_user

        if self.follow_up_date and timezone.is_naive(self.follow_up_date):
            self.follow_up_date = timezone.make_aware(self.follow_up_date)

        is_new = self._state.adding
        super().save(*args, **kwargs)

        if self.follow_up_date and not self.reminder_set:
            from .task import schedule_follow_up

            schedule_follow_up(self.id, days_before=1)

    @property
    def is_upcoming_follow_up(self):
        if self.follow_up_date:
            return self.follow_up_date > timezone.now()
        return False

    @property
    def days_until_follow_up(self):
        if self.follow_up_date:
            delta = self.follow_up_date.date() - timezone.now().date()
            return delta.days
        return None
