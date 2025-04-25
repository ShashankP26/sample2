from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CashVoucher

from django.db.models import F

@receiver(post_save, sender=CashVoucher)
def update_expense_on_approval(sender, instance, **kwargs):
    if instance.status == "approved":
        print("Signal triggered for voucher:", instance.voucher_number)  # Debugging print
        expense = instance.expense
        print(f"Expense before update: {expense.amount}")  # Debugging print
        expense.amount = F('amount') + instance.amount  # Use F expression for atomic update
        expense.save()
        print(f"Expense after update: {expense.amount}")  # Debugging print


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Expense, CashVoucher, Notification

# @receiver(post_save, sender=Expense)
# def notify_user_on_voucher_paid(sender, instance, created, **kwargs):
#     # Check if the Expense status is set to "paid" after save
#     if not created and instance.status == 'paid':
#         # Send notification to the user who created the Expense
#         Notification.objects.create(
#             user=instance.created_by,
#             message=f"Your voucher for {instance.item_name} has been marked as 'Paid'."
#         )

# @receiver(post_save, sender=CashVoucher)
# def notify_user_on_cash_voucher_paid(sender, instance, created, **kwargs):
#     # Check if the CashVoucher status is set to "approved" or "paid" after save
#     if not created and instance.status == 'approved':  # assuming 'approved' means the voucher is paid
#         # Send notification to the user who created the CashVoucher
#         Notification.objects.create(
#             user=instance.created_by,
#             message=f"Your cash voucher for {instance.item_name} has been approved and paid."
#         )