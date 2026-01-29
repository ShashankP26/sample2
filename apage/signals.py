from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ServiceReport, ServiceReportEditLog

@receiver(pre_save, sender=ServiceReport)
def track_service_report_changes(sender, instance, **kwargs):
    print(f"Signal triggered for ServiceReport: {instance}")

    if not instance.pk:  # Skip for new objects
        print("Skipping new instance")
        return

    try:
        original = ServiceReport.objects.get(pk=instance.pk)
    except ServiceReport.DoesNotExist:
        print("Original object does not exist")
        return

    user = getattr(instance, 'edited_by', None)
    if not user:
        print("No user associated with the edit")
        return

    # List of fields to exclude from tracking
    excluded_fields = ['client_signature', 'service_person_signature']

    # Track only fields that are not excluded
    tracked_fields = [
        field.name
        for field in sender._meta.fields
        if not field.auto_created and not field.is_relation and field.editable and field.name not in excluded_fields
    ]

    print("Tracked Fields:", tracked_fields)

    for field_name in tracked_fields:
        old_value = getattr(original, field_name, None)
        new_value = getattr(instance, field_name, None)
        print(f"Field: {field_name}, Old: {old_value}, New: {new_value}")

        if old_value != new_value:
            try:
                ServiceReportEditLog.objects.create(
                    report=instance,
                    edited_by=user,
                    field_changed=field_name,
                    old_value=str(old_value) if old_value is not None else "None",
                    new_value=str(new_value) if new_value is not None else "None",
                )
                print(f"Logged change for field: {field_name}")
            except Exception as e:
                print(f"Failed to log change for field '{field_name}': {e}")
