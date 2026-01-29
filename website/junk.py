def payable(request):
    users = User.objects.all()
    zones = Zone.objects.all()
    expenses = Expense.objects.none()  # Default empty queryset
    selected_user = None
    selected_zone = None
    selected_filter = request.POST.get('date_filter')  # Retrieve selected date filter
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    filtered_users = User.objects.none()  # Default empty queryset for filtered users
    total_amount_to_be_paid = 0
    min_date = None
    max_date = None

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        zone_id = request.POST.get('zone_id')

        # Base queryset for filtering
        queryset = Expense.objects.all()

        # Filter by zone (through UserProfile)
        if zone_id:
            selected_zone = Zone.objects.get(id=zone_id)
            users_in_zone = UserProfile.objects.filter(zone=selected_zone).values_list('user', flat=True)
            filtered_users = User.objects.filter(id__in=users_in_zone)  # Filter users by zone
            queryset = queryset.filter(created_by__in=users_in_zone)

        # Filter by user
        if user_id:
            selected_user = User.objects.get(id=user_id)
            queryset = queryset.filter(created_by=selected_user)

        # Apply custom date range filtering (based on date field)
        if from_date and to_date:
            queryset = queryset.filter(date__range=[from_date, to_date])

        # Apply predefined date filter (like last 15, 30, etc., days)
        elif selected_filter:
            try:
                days = int(selected_filter.split()[0])  # Extract number from "15 days" etc.
                filter_date = date.today() - timedelta(days=days)
                queryset = queryset.filter(date__gte=filter_date)
            except ValueError:
                pass  # Ignore invalid date_filter values

        # Update min and max dates for the date range filter
        if queryset.exists():
            min_date = queryset.earliest('date').date
            max_date = queryset.latest('date').date

        # Final expenses and total amount
       	expenses = queryset.filter(Q(proof_photo__gt='') | Q(transaction_option='voucher')).exclude(status='paid').filter(is_draft=False).filter(Q(cashvoucher__isnull=True) | Q(cashvoucher__status='approved'))
        total_amount_to_be_paid = sum(exp.amount or 0 for exp in expenses)


    context = {
        'users': users,
        'zones': zones,
        'expenses': expenses,
        'selected_user': selected_user,
        'selected_zone': selected_zone,
        'selected_filter': selected_filter,
        'from_date': from_date,
        'to_date': to_date,
        'filtered_users': filtered_users,
        'total_amount_to_be_paid': total_amount_to_be_paid,
        'min_date': min_date,
        'max_date': max_date,
    }
    return render(request, 'xp/payable.html', context)