from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Expense(models.Model):
    ITEM_TYPES = [
        ('fright_transportation', 'Fright/Transportation'),
        ('food_grocery', 'Food/Grocery'),
        ('fuel_oil', 'Fuel and Oil'),
        ('others', 'Others'),
        ('vendor', 'Vendor'),
        ('reimbursement', 'Reimbursement'),
        ('site_services', 'Site Services'),
        ('advances', 'Advances'),
        ('travelling', 'Travelling'),
        ('electricity_bill', 'Electricity Bill'),
        ('internet_bill', 'Internet Bill'),
        ('postage_telegram', 'Postage and Telegram'),
        ('machine_repair', 'Machine Repair and Maintenance'),
        ('conveyance', 'Conveyance'),
        ('stationary_printing', 'Stationary and Printing'),
        ('hospitality', 'Hospitality'),
    ]

    TRANSACTION_CATEGORY_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('debit_card', 'Debit Card'),
        ('credit_card', 'Credit Card'),
    ]

    PAYMENT_OPTIONS = [
    ('bill', 'Bill'),
    ('voucher', 'Voucher'),
    ('gst', 'GST'),
     ('2_wheeler', '2-Wheeler'),
    ('4_wheeler', '4-Wheeler'),
]

    # Model fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_expenses', null=True, blank=True)
    item_type = models.CharField(max_length=50, choices=ITEM_TYPES, blank=True, null=True)
    item_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    transaction_option = models.CharField(max_length=20, choices=PAYMENT_OPTIONS, null=True)
    bill_photo = models.FileField(upload_to='bills/', blank=True, null=True)
    voucher_number = models.CharField(max_length=100, blank=True, null=True)
    transaction_category = models.CharField(max_length=100, choices=TRANSACTION_CATEGORY_CHOICES, blank=True, null=True)
    internal_option = models.CharField(max_length=100, null=True, blank=True, default='abs')
    external_type = models.CharField(max_length=100, null=True, blank=True, default='legs')
    gst_photo = models.ImageField(upload_to='gst_photos/', null=True, blank=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, blank=True, null=True)
    proof_photo = models.FileField(upload_to='proofs/', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transaction_details = models.TextField(null=True, blank=True)
    evoucher_number = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    is_draft = models.BooleanField(default=False)
    
    km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Kilometers field
    conveyance = models.ForeignKey('Conveyance', on_delete=models.SET_NULL, null=True, blank=True)  # Use string for Conveyance

    # Method to calculate the amount based on km and vehicle type
    def calculate_amount(self):
        if self.conveyance and self.km is not None:
            return self.conveyance.price_per_km * self.km
        return None  # Return None if no calculation is required

    # Override save method to calculate amount conditionally
    def save(self, *args, **kwargs):
        # Calculate amount only if both conveyance and km are provided
        if self.conveyance and self.km is not None:
            self.amount = self.calculate_amount()
        super().save(*args, **kwargs)

    # Display format for the model instance
    def __str__(self):
        return f"{self.created_by} - {self.item_type}"


# BorrowedAmount Model
class BorrowedAmount(models.Model):

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='borrowed_amounts')
    borrowed_from = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.borrowed_from} - {self.amount}"

# CashVoucher Model
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class CashVoucher(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, null=True, blank=True)
    voucher_number = models.CharField(max_length=20, unique=True)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_to = models.CharField(max_length=25)
    item_name = models.CharField(max_length=255)
    transaction_date = models.DateField(null=True, blank=True)
    verified_by = models.CharField(max_length=255, null=True, blank=True)
    approved_by = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cash_vouchers', null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True, default='NONE')
    verified_at = models.DateTimeField(default=timezone.now, null=True, blank=True)  # Use timezone.now()
    proof_photo = models.FileField(upload_to='cashvoucher_proofs/', null=True, blank=True)

    

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Voucher #{self.voucher_number} - {self.status}"



from django.db import models
from django.conf import settings  # For referencing the custom user model

class Payment(models.Model):
    paid_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    from_date = models.DateField()  # Start date for the payment duration
    to_date = models.DateField()    # End date for the payment duration
    screenshot = models.ImageField(upload_to='payment_screenshots/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.paid_to} - {self.transaction_id}"
    

# models.py


# Check if the import is necessary and valid

# website/models.py

# website/models.py

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('unread', 'Unread'), ('read', 'Read')], default='unread')


from django.db import models

class Conveyance(models.Model):
    VEHICLE_TYPES = [
        ('2_wheeler', '2_Wheeler'),
        ('4_wheeler', '4_Wheeler'),
    ]
    
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)  # Price per kilometer

    def __str__(self):
        return f"{self.vehicle_type} - {self.price_per_km} per km"

from django.db import models
from django.contrib.auth.models import User

class AdvancePayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
    


class ProofPhoto(models.Model):
    expense = models.ForeignKey(Expense, related_name='proof_photos', on_delete=models.CASCADE)
    file = models.FileField(upload_to='proofs/')