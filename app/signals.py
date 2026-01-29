from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserActivityLog

@receiver(post_save, sender=User)
def log_user_activity(sender, instance, created, **kwargs):
    if created:
        action = 'added'  # Log user creation when the user is created
    else:
        action = 'modified'  # Log user modification when the user is updated

    # Log the action and store the hashed password from the User model
    UserActivityLog.objects.create(
        user=instance,
        action=action,
        password=instance.password  # This password is already hashed by Django
    )


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import GroupButton


@receiver(post_save, sender=Group)
def create_group_button(sender, instance, created, **kwargs):
    if created:  # If a new group is created
        # Make sure the group name is correctly formatted and passed
        url_name = f'admin:group_{instance.name.lower()}'
        GroupButton.objects.get_or_create(name=instance.name, url_name=url_name)
        print(f"Creating group button for {instance.name} with URL: {url_name}")



# ------------------------------------------------------------------MODULE VISIBILITY ------------------------------------------------------------

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ModuleVisibility

@receiver(post_save, sender=User)
def create_module_visibility(sender, instance, created, **kwargs):
    if created:
        ModuleVisibility.objects.create(user=instance)







