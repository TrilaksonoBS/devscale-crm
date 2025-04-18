from django.db import models

from .utils import genereate_id


class BaseModel(models.Model):
    id = models.CharField(
        max_length=255, primary_key=True, default=genereate_id, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
