from django.urls import path
from . import views 
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Home
    path('home', views.home, name="home"),

    # File Upload
    path('success/', views.success_view, name='success'),

    # Item Form
    path('item_form/', views.item_form, name='item_form'),


    # Cash Voucher
    path('cash_voucher/', views.cash_voucher, name='cash_voucher'),
    path('create-cash-voucher/', views.create_cash_voucher, name='create_cash_voucher'),
    path('cash_voucher/success/', views.success_view, name='cash_voucher_success'),
    path('approve-voucher/<str:voucher_number>/', views.approve_cash_voucher, name='approve_cash_voucher'),
    path('approved-vouchers/', views.approved_vouchers, name='approved_vouchers'),
    path('rejected-vouchers/', views.rejected_vouchers, name='rejected_vouchers'),
    path('reject/', views.reject_voucher, name='reject_voucher'),
    path('dashboard/', views.vouchers_dashboard, name='vouchers_dashboard'),
    path('payable/', views.payable, name='payable'),
    path('get_users_by_zone/', views.get_users_by_zone, name='get_users_by_zone'),
    
    

    # E-Voucher
    path('e-voucher/', views.e_voucher, name='e_voucher'),
    path('e-vouchers/', views.item_form, name='e_vouchers'),

    

    # Expense Management
    path('expense/form/', views.expense_form, name='expense_form'),
    path('expense/details/<int:expense_id>/', views.expense_details, name='expense_details'),

    path('expense_home/', views.expense_home, name='expense_home'),  # Expense home page

    # New Item and Cash Voucher Forms
    path("new-item-form/<int:user_id>/", views.new_item_form, name="new_item_form"),
    path('new-cash-voucher-form/', views.new_cash_voucher_form, name='new_cash_voucher_form'),  # Renamed for clarity

    # Edit Item and Cash Voucher

    path('edit-cash-voucher/<int:voucher_id>/', views.edit_cash_voucher_form, name='edit_cash_voucher_form'),

    # Voucher Data
    path('get_voucher_data/', views.get_voucher_data, name='get_voucher_data'),
    path('draft-vouchers/', views.draft_vouchers, name='draft_vouchers'),


    # Search
    path('search/', views.search_view, name='search_view'),

    # Update Item
    path('update_item/', views.update_item, name='update_item'),
    path('voucher-summary/', views.transaction, name='transaction'),

    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('export/', views.export_vouchers, name='export_vouchers'),
    path('export-cash-vouchers/', views.export_cash_vouchers, name='export_cash_vouchers'),

    path('payable/', views.payable, name='payable'),
    path('pay_now/<int:user_id>/', views.pay_now, name='pay_now'),
    path('process_payment/', views.process_payment, name='process_payment'),
    # Add a success page for when the payment is processed
    path('payment_success/', views.payment_success, name='payment_success'),
    path('user-payments/', views.payments, name='payments'),
   
    # path('payment-history/', views.payment_history, name='payment_history'),
    path('export_payments/', views.export_payments, name='export_payments'),
    path('get-monthwise-data/', views.get_monthwise_data, name='get_monthwise_data'),
    

    # path('scan-amount/', views.scan_amount, name='scan_amount'),
    # path('extract_amount/', views.extract_amount, name='extract_amount'),
    #  path('extract-amount-from-bill/', views.extract_amount_from_bill_view, name='extract-amount-from-bill'),


    # path('process-bill-photo/', process_bill_photo, name='process-bill-photo'),
    # path('process-gst-photo/', process_gst_photo, name='process-gst-photo'),
    # path('process-uploaded-image/', views.process_uploaded_image, name='process_uploaded_image'),
    path('process-photo/', views.process_photo, name='process_photo'),  # Add this line
    path('upload-temporary/', views.upload_temporary, name='upload_temporary'),
    path('get_price_per_km/', views.get_price_per_km, name='get_price_per_km'),
    path('test/', views.test, name='test'),
    path('erp-software/', views.erp_software, name='erp_software'), 

    
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)