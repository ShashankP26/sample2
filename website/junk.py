def edit_item(request, item_id):
    expense = get_object_or_404(Expense, id=item_id)
    users = User.objects.all()
    is_draft = False
    

    if request.method == "POST":
        # Retrieve form data
        item_type = request.POST.get('item_type')
        item_name = request.POST.get('item_name')
        payment_category = request.POST.get('payment_category')
        transaction_category = request.POST.get('transaction_category')
        amount = request.POST.get('amount')
        payment_mode = request.POST.get('payment_mode')
        transaction_date = request.POST.get('transaction_date')
        evoucher_number = request.POST.get('e_voucher_number')
        proof_photo = request.FILES.get("proof_photo")
        borrowed_amounts = request.POST.getlist("borrowed_amounts[]")
        borrowed_froms = request.POST.getlist("borrowed_froms[]")
        draft_statuss = request.POST.get('draft_status') 

        draft_status = request.POST.get('draft_status', 'false')  # Default to 'false' if not provided

        is_draft = draft_status.lower() == 'true'

        # Validate the amount
        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid amount value.'})

        # Update fields for the expense
        expense.item_type = item_type
        expense.item_name = item_name
        expense.payment_category = payment_category
        expense.transaction_category = transaction_category
        expense.amount = amount
        expense.payment_mode = payment_mode
        expense.transaction_date = transaction_date
        expense.evoucher_number = evoucher_number
        expense.proof_photo = proof_photo
        expense.is_draft=is_draft

        # Handle borrowed amounts
        borrowed_froms_filtered = [id for id in borrowed_froms if id.strip()]
        remaining_amount = amount

        # Create BorrowedAmount instances and replicate vouchers for borrowed users
        borrowed_amount_objects = []
        for borrowed_amount, borrowed_from in zip(borrowed_amounts, borrowed_froms_filtered):
            if borrowed_amount and borrowed_from:
                borrowed_amount = Decimal(borrowed_amount)  # Convert borrowed amount to Decimal
                user = User.objects.get(id=borrowed_from)  # Get the user who lent the amount

                # If borrowed amount is less than or equal to remaining amount, process it
                if borrowed_amount <= remaining_amount:
                    borrowed_amount_object = BorrowedAmount(
                        expense=expense,
                        borrowed_from=user,
                        amount=borrowed_amount
                    )
                    borrowed_amount_objects.append(borrowed_amount_object)

                    # Replicate the voucher for the selected user (User 2)
                    Expense.objects.create(
                        created_by=user,  # User 2 is the one from whom the money is borrowed
                        item_type=item_type,
                        item_name=f"Borrowed - {item_name}",
                        transaction_option='voucher',  # Assuming it's a voucher transaction
                        transaction_category="internal",  # This is an internal transaction for User 2
                        amount=borrowed_amount,
                        payment_mode=payment_mode,
                        voucher_number=expense.voucher_number,  # Use the same voucher number for User 2
                        evoucher_number=evoucher_number,
                        proof_photo=None,  # No proof photo for borrowed amount
                        transaction_date=transaction_date,
                        is_draft=is_draft,
                    )

                    # Update the remaining amount
                    remaining_amount -= borrowed_amount
                else:
                    # If borrowed amount exceeds the remaining amount, skip this entry
                    continue

        # Save the BorrowedAmount instances in bulk
        BorrowedAmount.objects.bulk_create(borrowed_amount_objects)

        # If any remaining amount exists for User 1, update it
        if remaining_amount > 0:
            expense.amount = remaining_amount
            expense.save()

        # Save the updated expense
        expense.save()
        print(f"status",expense.is_draft)
        # Redirect to the item form page
        if is_draft:
            return redirect("draft_vouchers")  # Redirect to the draft vouchers list page

        return redirect('item_form')  # Adjust to your correct URL name

    # Handle GET request, prefill form with existing data
    return render(request, 'xp/edit_item.html', {
        'expense': expense,  # Pass the expense object to the template
        'evoucher_number': expense.evoucher_number,
        'users': users,
    })





    def transaction(request):
    user = request.user
    # Filter
    transaction_date_from = request.GET.get('transaction_date_from', None)
    transaction_date_to = request.GET.get('transaction_date_to', None)
    item_type_filter = request.GET.get('item_type', '')
    search_query = request.GET.get('search', '').strip()
    selected_user_id = request.GET.get('user_id', None)  # Capture user selection
    users = User.objects.all()

    # Base queryset
    if user.is_staff or user.is_superuser:
        expenses = Expense.objects.all()  # Admin or staff see all vouchers
    else:
        # Include vouchers created by the user and internal vouchers assigned to the user
        expenses = Expense.objects.filter(
    created_by=user
) | Expense.objects.filter(
    transaction_category='internal', internal_option__icontains=user.username
)
    expenses = expenses.order_by('-transaction_date')

    # Filter by selected user (if any)
    if selected_user_id:
        expenses = expenses.filter(created_by_id=selected_user_id)  # Filter by selected user

    # Apply other filters
    if item_type_filter:
        expenses = expenses.filter(item_type=item_type_filter)

    if transaction_date_from:
        try:
            transaction_date_from = datetime.strptime(transaction_date_from, '%Y-%m-%d').date()
            expenses = expenses.filter(transaction_date__gte=transaction_date_from)
        except ValueError:
            pass
    if transaction_date_to:
        try:
            transaction_date_to = datetime.strptime(transaction_date_to, '%Y-%m-%d').date()
            expenses = expenses.filter(transaction_date__lte=transaction_date_to)
        except ValueError:
            pass

    # Apply search query
    if search_query:
        expenses = expenses.filter(
            Q(evoucher_number__icontains=search_query) |
            Q(item_type__icontains=search_query) |
            Q(transaction_date__icontains=search_query) |
            Q(transaction_details__icontains=search_query)
        )

    # Prepare data for the summary
    summary_data = []
    user_balances = defaultdict(int)

    for index, expense in enumerate(expenses.distinct()):
        evoucher_number = expense.evoucher_number if expense.evoucher_number else ''
        
        # Format internal users with underscores
        if expense.transaction_category == 'internal' and expense.internal_option:
            internal_users = "_".join(expense.internal_option.split(","))
            internal_or_external = f"int_{internal_users}"
        else:
            internal_or_external = "ext"

        summary = f"{evoucher_number}_{internal_or_external}"
        debit = expense.amount
        credit = expense.amount if expense.status == 'paid' else 0
        user_balances[expense.created_by] += credit - debit
        current_balance = user_balances[expense.created_by]

        summary_data.append({
            'slno': index + 1,
            'transaction_date': expense.transaction_date,
            'summary': summary,
            'debit': debit,
            'credit': credit if credit else "",
            'balance': current_balance,
            'created_by': expense.created_by,

        })

    # Handle Export Requests
    export_type = request.GET.get('export', '').lower()
    if export_type == 'csv':
        return export_csv(summary_data)
    elif export_type == 'xlsx':
        return export_xlsx(summary_data)
    elif export_type == 'pdf':
        return export_pdf(summary_data)

    # Context for rendering the template
    context = {
        'summary_data': summary_data,
        'transaction_date_from': transaction_date_from,
        'transaction_date_to': transaction_date_to,
        'item_types': Expense.objects.values_list('item_type', flat=True).distinct(),
        'search_query': search_query,
        'users': users,
        'selected_user_id': selected_user_id,  # Pass the selected user ID to the template
    }

    return render(request, 'xp/voucher_summary.html', context)