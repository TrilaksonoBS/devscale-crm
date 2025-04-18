from django.apps import AppConfig


class InteractionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.interactions"

    def ready(self):
        import apps.interactions.task  # This ensures tasks are registered
