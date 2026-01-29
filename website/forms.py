from django import forms
from .models import Expense, Conveyance

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'item_type',
            'item_name',
            'transaction_option',
            'bill_photo',
            'gst_photo',
            'voucher_number',
            'transaction_category',
            'internal_option',
            'external_type',
            'payment_mode',
            'proof_photo',
            'amount',
            'evoucher_number',
            'transaction_date',
        ]

    # Transaction choices for categorizing the transaction
    TRANSACTION_CHOICES = [
        ('external', 'External'),
        ('internal', 'Internal'),
    ]

    TRANSACTION_OPTION_CHOICES = [
        ('bill', 'Bill'),
        ('voucher', 'Voucher'),
        ('gst', 'GST'),
         ('2_wheeler', '2-Wheeler'),
        ('4_wheeler', '4-Wheeler'),
    ]

    ITEM_TYPE_CHOICES = [
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
        ('machine_repair', 'Machine Repair and Maintenance - Machinery'),
        ('conveyance', 'Conveyance'),
        ('stationary_printing', 'Stationary and Printing'),
        ('hospitality', 'Hospitality'),
    ]
    

    # Define form fields with appropriate choices
    item_type = forms.ChoiceField(choices=ITEM_TYPE_CHOICES, required=True)
    item_name = forms.CharField(max_length=255, required=True)
    transaction_option = forms.ChoiceField(choices=TRANSACTION_OPTION_CHOICES, required=True)
    transaction_category = forms.ChoiceField(choices=TRANSACTION_CHOICES, required=True)
    internal_option = forms.ChoiceField(choices=[], required=False)
    external_type = forms.CharField(max_length=255, required=False)  # renamed to match model field
    payment_mode = forms.CharField(max_length=100, required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    kilometers = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    vehicle_type = forms.ChoiceField(
        choices=[('2_wheeler', '2-Wheeler'), ('4_wheeler', '4-Wheeler')],
        required=False
    )

    # Optional fields depending on transaction option
    bill_photo = forms.ImageField(required=False)
    gst_photo = forms.ImageField(required=False)
    voucher_number = forms.CharField(max_length=100, required=False)
    proof_photo = forms.ImageField(required=False)
    transaction_date = forms.DateField(required=True)
def __init__(self, *args, **kwargs):
    internal_users = kwargs.pop('internal_users', [])
    super().__init__(*args, **kwargs)
    self.fields['internal_option'].choices = [('', 'Select Name')] + [(user.username, user.username) for user in internal_users]

def clean(self):
    cleaned_data = super().clean()

    # Handle draft status
    status = cleaned_data.get('status')
    if status == 'draft':
        return cleaned_data

    # Handle dynamic visibility and validation for form fields
    transaction_option = cleaned_data.get('transaction_option')

    # Field validations for specific transaction options
    if transaction_option == 'bill' and not cleaned_data.get('bill_photo'):
        raise forms.ValidationError("Bill photo is required for 'Bill' option.")
    if transaction_option == 'gst' and not cleaned_data.get('proof_photo'):
        raise forms.ValidationError("Proof photo is required for 'GST' option.")
    if transaction_option == 'voucher' and not cleaned_data.get('voucher_number'):
        raise forms.ValidationError("Voucher number is required for 'Voucher' option.")

    # Additional validations for transaction_category
    transaction_category = cleaned_data.get('transaction_category')

    if transaction_category == 'internal' and not cleaned_data.get('internal_option'):
        raise forms.ValidationError("Internal option is required for 'Internal' category.")
    if transaction_category == 'external' and not cleaned_data.get('external_type'):
        raise forms.ValidationError("External type is required for 'External' category.")

    # Conveyance-specific validation and amount calculation
    item_type = cleaned_data.get('item_type')
    vehicle_type = cleaned_data.get('vehicle_type')
    kilometers = cleaned_data.get('kilometers')

    print(f"Item Type: {item_type}")
    print(f"Vehicle Type: {vehicle_type}")
    print(f"Kilometers: {kilometers}")

    if item_type == 'conveyance':
        if not vehicle_type:
            raise forms.ValidationError("Vehicle type is required for 'Conveyance'.")
        if not kilometers or kilometers <= 0:
            raise forms.ValidationError("Kilometers must be greater than zero for 'Conveyance'.")

        # Fetch price per km from the Conveyance model
        # Fetch the conveyance object based on selected vehicle type
        try:
            conveyance = Conveyance.objects.get(vehicle_type=vehicle_type)
            rate_per_km = conveyance.price_per_km
            print(f"Rate per Kilometer for {vehicle_type}: {rate_per_km}")
            # Now, you can use the rate_per_km to calculate the amount
            cleaned_data['amount'] = kilometers * rate_per_km
            print(f"Calculated Amount: {cleaned_data['amount']}")
        except Conveyance.DoesNotExist:
            raise forms.ValidationError(f"Price per kilometer is not set for {vehicle_type}.")

        return cleaned_data

from django import forms
from .models import CashVoucher
from django.contrib.auth.models import User

class CashVoucherForm(forms.ModelForm):
    class Meta:
        model = CashVoucher
        fields = ['voucher_number', 'amount', 'paid_to', 'item_name', 'transaction_date','verified_at','proof_photo']

    # Accept the user as an additional argument when initializing the form
    def __init__(self, *args, user=None, **kwargs):
        self.user = user  # Store the user for later use
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:  # Assign the logged-in user to created_by
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance
    

# from django import forms
# from .models import BorrowedAmount
# from django.contrib.auth.models import User

# class BorrowedAmountForm(forms.ModelForm):
#     user = forms.ModelChoiceField(queryset=User.objects.all(), required=True)
#     borrowed_amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

#     class Meta:
#         model = BorrowedAmount
#         fields = ['user', 'borrowed_amount']

