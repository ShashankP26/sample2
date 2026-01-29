from django.test import TestCase
from website.models import CashVoucher, Expense
from datetime import date

class SignalTest(TestCase):
    def test_update_expense_on_approval(self):
        # Create an Expense instance with a transaction date
        expense = Expense.objects.create(amount=100, transaction_date=date.today())  # Provide a valid date
        voucher = CashVoucher.objects.create(amount=50, status="pending", expense=expense)
        
        # Change status to approved
        voucher.status = "approved"
        voucher.save()

        # Verify that the expense amount is updated after the signal is triggered
        expense.refresh_from_db()
        self.assertEqual(expense.amount, 150)  # Expecting the updated amount to be 150