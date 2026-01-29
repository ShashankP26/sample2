from datetime import date, datetime
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from website.models import CashVoucher, Expense  # Adjust the import paths
from django.db import models

def dashboard_data(request):
    if not request.user.is_authenticated:  # Avoid running for anonymous users
        return {}

    user = request.user

    # Get date filters from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Default to the current month if no filters are provided
    if not from_date or not to_date:
        today = date.today()
        first_day = today.replace(day=1)
        from_date = first_day
        to_date = today

    # Convert to date objects if they are strings
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

    # Filter vouchers and expenses based on user role and date range
    if user.is_staff:
        vouchers = CashVoucher.objects.filter(date__range=(from_date, to_date))
        expenses = Expense.objects.filter(date__range=(from_date, to_date))
    else:
        vouchers = CashVoucher.objects.filter(created_by=user, date__range=(from_date, to_date))
        expenses = Expense.objects.filter(created_by=user, date__range=(from_date, to_date))

    # Calculate totals
    total_claiming_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_claiming_amount_cv = vouchers.aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate totals for the monthly report
    vouchers_by_month = vouchers.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_claimed=Sum('amount'),
        total_paid=Sum('amount', filter=Q(status='paid'))
    ).order_by('month')

    months_list = []
    claimed_amounts = []
    paid_amounts = []

    for voucher in vouchers_by_month:
        months_list.append(voucher['month'].strftime('%b %Y'))
        claimed_amounts.append(voucher['total_claimed'])
        paid_amounts.append(voucher['total_paid'])
       
    item_type_counts = Expense.objects.values('item_type').annotate(count=models.Count('item_type'))

    item_type_totals = {
        'Fright/Transportation': Expense.objects.filter(item_type='Fright/Transportation').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Fuel and Oil': Expense.objects.filter(item_type='Fuel and Oil').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Food/Grocery': Expense.objects.filter(item_type='Food/Grocery').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Others': Expense.objects.filter(item_type='others').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Vendor': Expense.objects.filter(item_type= 'vendor').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Reimbursement': Expense.objects.filter(item_type= 'reimbursement').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Site_services': Expense.objects.filter(item_type= 'site_services').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Advances': Expense.objects.filter(item_type= 'advances').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Travelling': Expense.objects.filter(item_type= 'travelling').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Electricity_bill': Expense.objects.filter(item_type= 'electricity_bill').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Internet_bill': Expense.objects.filter(item_type= 'internet_bill').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Postage_telegram': Expense.objects.filter(item_type= 'postage_telegram').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Machine_repair': Expense.objects.filter(item_type= 'machine_repair').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Conveyance': Expense.objects.filter(item_type= 'conveyance').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Stationary_printing': Expense.objects.filter(item_type= 'stationary_printing').aggregate(Sum('amount'))['amount__sum'] or 0,
        'Hospitality': Expense.objects.filter(item_type= 'hospitality').aggregate(Sum('amount'))['amount__sum'] or 0,
        
       
    }

    # Create a dictionary of counts
    item_type_data = {
        'fright_transportation': 0,
        'fuel_oil': 0,
        'food_grocery': 0,
        'others': 0,
        'vendor': 0,
        'reimbursement': 0,
        'site_services': 0,
        'advances': 0,
        'travelling': 0,
        'electricity_bill': 0,
        'internet_bill': 0,
        'postage_telegram': 0,
        'machine_repair': 0,
        'conveyance': 0,
        'stationary_printing': 0,
        'hospitality': 0,
    }

    # Fill item_type_data with counts
    for entry in item_type_counts:
        item_type_data[entry['item_type']] = entry['count']

    # Return the context
    return {
        'dashboard_data': {
            'from_date': from_date,
            'to_date': to_date,
            'total_claiming_amount': total_claiming_amount,
            'total_claiming_amount_cv': total_claiming_amount_cv,
            'months_list': months_list,
            'claimed_amounts': claimed_amounts,
            'paid_amounts': paid_amounts,
            'item_type_data': item_type_data,
            'item_type_totals': item_type_totals,
        }
    }


from django.shortcuts import get_object_or_404
from .models import Notification, User, CashVoucher, Expense
from datetime import datetime

def pay_now_context(request):
    payment_details = None
    selected_user = None
    expenses = None
    total_amount_to_be_paid = None
    transaction_id = None
    from_date = None
    to_date = None
    selected_filter = None

    # If 'user_id' is provided in the request
    user_id = request.GET.get('user_id', None)
    if user_id:
        selected_user = get_object_or_404(User, id=user_id)
        expenses = Expense.objects.filter(created_by=selected_user, status="pending")
        total_amount_to_be_paid = request.GET.get('total_amount_to_be_paid')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        selected_filter = request.GET.get('selected_filter')

        # Logic to generate transaction ID (XPTR+YY+M+counter)
        current_year = str(datetime.now().year)[2:]
        current_month = str(datetime.now().month).zfill(2)  # Ensure month is two digits
        counter = CashVoucher.objects.filter(created_by=selected_user).count() + 1  # Add 1 to the count
        counter_formatted = f"{counter:04d}"  # Zero-pad the counter to 4 digits
        transaction_id = f"XPTR{current_year}{current_month}{counter_formatted}"

    # If the form is submitted
    if request.method == 'POST':
        # Get form data
        transaction_id = request.POST.get('transaction_id')
        amount = request.POST.get('amount')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        screenshot = request.FILES.get('screenshot')

        # Prepare payment details
        payment_details = {
            'transaction_id': transaction_id,
            'amount': amount,
            'from_date': from_date,
            'to_date': to_date,
            'screenshot': screenshot,
        }

    return {
        'selected_user': selected_user,
        'expenses': expenses,
        'total_amount_to_be_paid': total_amount_to_be_paid,
        'transaction_id': transaction_id,
        'from_date': from_date,
        'to_date': to_date,
        'selected_filter': selected_filter,
        'payment_details': payment_details,
    }

from .models import CashVoucher
from datetime import datetime

def generate_voucher_number(request):
    # Get the current date
    current_date = datetime.now()
    
    # Format the year as 'yy' and month as 'mm'
    year_month = current_date.strftime('%y%m')  # 'yy' format for year and 'mm' for month
    
    # Define the voucher counter. In practice, this would come from your database, and you would
    # increment the counter for each new voucher in the same month.
    # For demonstration purposes, we are assuming the counter starts at 1.
    last_voucher = CashVoucher.objects.filter(voucher_number__startswith=f"XPCV{year_month}").order_by('voucher_number').last()

    if last_voucher:
        # Extract the number part from the last voucher and increment it
        last_number = int(last_voucher.voucher_number[-4:])
        next_number = last_number + 1
    else:
        # If no voucher exists for this month, start from 1
        next_number = 1


    counter_str = str(next_number).zfill(4)

    # Combine everything into the final voucher number
    voucher_number = f"XPCV{year_month}{counter_str}"
    
    return {'voucher_number': voucher_number}


# website/context_processors.py

# # In context processor
# def user_notifications(request):
#     if request.user.is_authenticated:
#         notifications = Notification.objects.filter(user=request.user, status='unread')
#         return {'user_notifications': notifications}
#     return {'user_notifications': []}

from .models import Notification

def notifications(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        if request.user.is_superuser:  # For admin users, get all notifications
            notifications = Notification.objects.all().order_by('-created_at').values('id', 'title', 'message', 'status', 'created_at')
        else:  # For regular users, filter by the current user (if notifications are user-specific)
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at').values('id', 'title', 'message', 'status', 'created_at')

        # Calculate unread notifications count
        unread_count = notifications.filter(status='unread').count()
    else:
        # If the user is not authenticated, return an empty list and count
        notifications = []
        unread_count = 0

    # Return notifications and unread_count as part of the context
    return {
        'notifications': list(notifications),
        'unread_count': unread_count,
    }