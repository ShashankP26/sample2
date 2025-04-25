from .models import ConfirmedOrderFollowUp, FollowUp
from django.utils import timezone
from datetime import timedelta

from itertools import chain

from itertools import chain
from django.db.models import Value, CharField

def followups_context(request):
    # Get today's date and the date one day before
    today = timezone.localdate()
    one_day_before = today - timedelta(days=1)

    # Query follow-ups and add a 'type' field
    followups_today = FollowUp.objects.filter(fodate=today).order_by('-fodate', '-fotime').annotate(type=Value('regular', output_field=CharField()))
    followups_one_day_before = FollowUp.objects.filter(fodate=one_day_before).order_by('-fodate', '-fotime').annotate(type=Value('regular', output_field=CharField()))
    followups = followups_today | followups_one_day_before

    # Query confirmed order follow-ups and add a 'type' field
    confirmed_followups_today = ConfirmedOrderFollowUp.objects.filter(fodate=today).order_by('-fodate', '-fotime').annotate(type=Value('confirmed', output_field=CharField()))
    confirmed_followups_one_day_before = ConfirmedOrderFollowUp.objects.filter(fodate=one_day_before).order_by('-fodate', '-fotime').annotate(type=Value('confirmed', output_field=CharField()))

    # Combine the querysets into a single iterable
    confirmed_followups = confirmed_followups_today | confirmed_followups_one_day_before
    all_followups = chain(followups, confirmed_followups)


    # Total count
    length = len(followups) + len(confirmed_followups)

    return {
        'followupss': all_followups,  # Combined follow-ups
        'length': length,  # Total count
    }

