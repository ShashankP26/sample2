from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone

from apage.models import SiteVisitSchedule, ServiceReport
from website.fcm import send_push_fcm


class Command(BaseCommand):
    help = "Send site visit reminder notifications (3 days before due)"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        target_date = today + timedelta(days=3)

        schedules = SiteVisitSchedule.objects.select_related("site").filter(
            next_due=target_date
        )

        sent = 0

        for schedule in schedules:
            site = schedule.site

            # ✅ FIND LAST SERVICE REPORT FOR THIS SITE
            last_report = (
                ServiceReport.objects
                .filter(site=site, created_by__isnull=False)
                .order_by("-created_date")
                .first()
            )

            if not last_report:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping site '{site.name}' (no service report found)"
                    )
                )
                continue

            user = last_report.created_by

            title = "Site Visit Reminder"
            body = (
                f"Next visit for site '{site.name}' is due on "
                f"{schedule.next_due.strftime('%d %b %Y')}"
            )

            send_push_fcm(user, title, body)
            sent += 1

        self.stdout.write(
            self.style.SUCCESS(f"Sent {sent} site visit reminders")
        )