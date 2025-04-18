import logging
from datetime import timedelta

from django.utils import timezone
from huey.contrib.djhuey import task

logger = logging.getLogger("huey")


@task()
def send_follow_up_reminder(interaction_id):
    try:
        from apps.interactions.models import Interaction

        interaction = Interaction.objects.get(id=interaction_id)

        logger.info(
            f"Reminder sent to {interaction.customer} for interaction: {interaction.summary}"
        )

        interaction.reminder_set = True
        interaction.save()

        return f"Sent reminder for interaction {interaction_id} - customer: {interaction.customer} - summary: {interaction.summary}"

    except Exception as e:
        logger.error(f"Error sending reminder: {str(e)}")
        return f"Failed to send reminder for interaction {interaction_id} - error: {str(e)}"


@task()
def schedule_follow_up(interaction_id, days_before=1):
    try:
        from apps.interactions.models import Interaction

        interaction = Interaction.objects.get(id=interaction_id)

        if not interaction.follow_up_date:
            logger.info(f"No follow-up date set for interaction {interaction_id}")
            return None

        follow_up_date = timezone.localtime(interaction.follow_up_date)
        now = timezone.localtime(timezone.now())

        reminder_delta = timedelta(days=days_before)
        reminder_time = timezone.localtime(follow_up_date - reminder_delta)

        if reminder_time <= now:
            logger.info(
                f"Follow-up date for interaction {interaction_id} is imminent or in the past. Sending reminder now."
            )
            send_follow_up_reminder(interaction_id)
        else:
            logger.info(
                f"Follow-up date for interaction {interaction_id} is in the future. Reminder scheduled for {reminder_time}"
            )

        interaction.reminder_set = True
        interaction.save(update_fields=["reminder_set"])

        return f"Scheduled follow-up for interaction {interaction_id}"

    except Exception as e:
        logger.error(f"Error scheduling follow-up: {str(e)}")
        return f"Failed to schedule follow-up for interaction {interaction_id} - error: {str(e)}"


@task()
def daily_summary():
    try:
        from apps.interactions.models import Interaction

        today = timezone.now().date()
        next_week = today + timedelta(days=7)

        interactions = Interaction.objects.filter(
            follow_up_date__date__range=(today, next_week)
        ).select_related("customer")

        if interactions.exists():
            logger.info(f"Daily summary for {today}:")
            for interaction in interactions:
                logger.info(
                    f"Interaction ID: {interaction.id} - Customer: {interaction.customer} - Summary: {interaction.summary}"
                )
        else:
            logger.info(f"No interactions found for {today}")

    except Exception as e:
        logger.error(f"Error generating daily summary: {str(e)}")
        return f"Failed to generate daily summary - error: {str(e)}"

    return "Daily summary generated successfully"
