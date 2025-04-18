from datetime import timedelta

import bson
from django.utils import timezone


def genereate_id():
    return str(bson.ObjectId())


def get_date_range_from_request(request, default_days=30):
    try:
        end_date = request.GET.get("end_date")
        start_date = request.GET.get("start_date")

        if end_date:
            end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date = timezone.now().date()

        if start_date:
            start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = end_date - timedelta(days=default_days)

        if start_date > end_date:
            start_date = end_date

        return start_date, end_date

    except (ValueError, TypeError):
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=default_days)

        return start_date, end_date


def get_upcoming_tasks(default_days=7):
    from apps.interactions.models import Interaction

    today = timezone.now().date()
    end_date = today + timedelta(days=default_days)

    return Interaction.objects.filter(follow_up_date__range=(today, end_date)).order_by(
        "follow_up_date"
    )
