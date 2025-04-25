from collections import defaultdict
import decimal
from importlib.metadata import files
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from requests import request
from .models import BorrowedAmount, Conveyance, Expense, Notification, ProofPhoto
from django.core.files.storage import FileSystemStorage  # Added for file storage handling
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, redirect
from .forms import ExpenseForm
from pytesseract import Output


def success_view(request):
    return render(request, 'xp/success.html')  # Success page after form submission

def home(request):
    print("Home entrd")
    return render(request, 'xp/home.html')  

def base(request):

    return render(request, 'xp/base.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Q
from .models import Expense, CashVoucher
import logging



def item_form(request):
    user = request.user
    search_query = request.GET.get('q', '').strip()
    transaction_date_from = request.GET.get('transaction_date_from', None)
    transaction_date_to = request.GET.get('transaction_date_to', None)
    item_type_filter = request.GET.get('item_type', '')
    sort_by_item_type = request.GET.get('sort_by_item_type', '0')
    logger = logging.getLogger(__name__)

    # Logging user information
    logger.debug(f"User: {user.username}, is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")
    logger.debug(f"Search Query: {search_query}")
    logger.debug(f"Date Range: From {transaction_date_from} to {transaction_date_to}")

    # Base queryset based on user role
    if user.is_staff or user.is_superuser:
        expenses = Expense.objects.all()  # Admin or staff see all expenses
    else:
        # For regular users, fetch only their own expenses or internal transactions
        expenses = Expense.objects.filter(
            Q(created_by=user) |  # Expenses created by this user
            Q(transaction_category='internal', internal_option=user.username) |  # Internal transactions where this user is involved
            Q(transaction_category='internal', internal_option__in=[user.username])  # Internal transactions where this user is the payer
        )
        logger.debug("User viewing their own and assigned internal expenses")

    # Apply item type filter if selected
    if item_type_filter:
        expenses = expenses.filter(item_type=item_type_filter)
    
    # Apply date range filters
    if transaction_date_from:
        try:
            transaction_date_from = datetime.strptime(transaction_date_from, '%Y-%m-%d').date()
            expenses = expenses.filter(transaction_date__gte=transaction_date_from)
        except ValueError:
            logger.warning("Invalid format for 'transaction_date_from'")
    if transaction_date_to:
        try:
            transaction_date_to = datetime.strptime(transaction_date_to, '%Y-%m-%d').date()
            expenses = expenses.filter(transaction_date__lte=transaction_date_to)
        except ValueError:
            logger.warning("Invalid format for 'transaction_date_to'")
    
    # Apply search query
    if search_query:
        expenses = expenses.filter(
            Q(item_type__icontains=search_query) |
            Q(item_name__icontains=search_query) |
            Q(transaction_category__icontains=search_query) |
            Q(external_type__icontains=search_query) |
            Q(internal_option__icontains=search_query) |
            Q(payment_mode__icontains=search_query) |
            Q(amount__icontains=search_query) |
            Q(transaction_date__icontains=search_query)|
            Q(created_by__username__icontains=search_query)
        )

    # Order results by `item_type` and `id`
    if sort_by_item_type == '1':  # If `sort_by_item_type` query param is 1
        expenses = expenses.order_by('item_type', '-id')
    else:
        expenses = expenses.order_by('-id')

    # Approved cash vouchers for reference (if needed)
    approved_vouchers = CashVoucher.objects.filter(status='approved')

    # Generate a new eVoucher number if required
    evoucher_number = generate_evoucher_number()

    # Filter expenses that are not drafts (is_draft=False)
    expenses = expenses.filter(is_draft=False).order_by('-evoucher_number')
    conveyance_vehicle_types = [option.vehicle_type for option in Conveyance.objects.all()]

    # Context for rendering the template
    context = {
        'evoucher_number': evoucher_number,
        'current_date': datetime.today().date(),
        'expenses': expenses,
        'approved_vouchers': approved_vouchers,
        'transaction_date_from': transaction_date_from,
        'transaction_date_to': transaction_date_to,
        'item_types': Expense.objects.values_list('item_type', flat=True).distinct(),
        'sort_by_item_type': sort_by_item_type,
    }

    return render(request, 'xp/item_form.html', context)

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

import csv
from django.http import HttpResponse

def export_csv(summary_data):
    # Create a response object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="voucher_summary.csv"'

    writer = csv.writer(response)
    # Write header row
    writer.writerow(['SLNO', 'User', 'Transaction Date', 'Summary', 'Debit', 'Credit', 'Balance'])

    # Write data rows
    for item in summary_data:
        writer.writerow([
            item['slno'],
            item['created_by'].username,
            item['transaction_date'],
            item['summary'],
            item['debit'],
            item['credit'],
            item['balance']
        ])
    
    return response

from openpyxl import Workbook
from django.http import HttpResponse

def export_xlsx(summary_data):
    # Create a response object with Excel content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="voucher_summary.xlsx"'

    # Create a workbook and a worksheet
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Voucher Summary'

    # Write header row
    headers = ['SLNO', 'User', 'Transaction Date', 'Summary', 'Debit', 'Credit', 'Balance']
    worksheet.append(headers)

    # Write data rows
    for item in summary_data:
        worksheet.append([
            item['slno'],
            item['created_by'].username,
            item['transaction_date'],
            item['summary'],
            item['debit'],
            item['credit'],
            item['balance']
        ])

    # Save workbook to the response object
    workbook.save(response)
    
    return response

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def export_pdf(summary_data):
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create a canvas object to generate the PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set font
    c.setFont("Helvetica", 10)

    # Write headers
    headers = ['SLNO', 'User', 'Transaction Date', 'Summary', 'Debit', 'Credit', 'Balance']
    x_offset = 50
    y_offset = height - 40

    for i, header in enumerate(headers):
        c.drawString(x_offset + i * 90, y_offset, header)
    
    y_offset -= 20  # Move to the next line for data rows

    # Write data rows
    for item in summary_data:
        c.drawString(x_offset, y_offset, str(item['slno']))
        c.drawString(x_offset + 90, y_offset, item['created_by'].username)
        c.drawString(x_offset + 180, y_offset, str(item['transaction_date']))
        c.drawString(x_offset + 270, y_offset, item['summary'])
        c.drawString(x_offset + 360, y_offset, str(item['debit']))
        c.drawString(x_offset + 450, y_offset, str(item['credit']))
        c.drawString(x_offset + 540, y_offset, str(item['balance']))
        y_offset -= 20

    # Save the PDF
    c.showPage()
    c.save()

    # Return the generated PDF as a response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="voucher_summary.pdf"'

    return response
def update_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('id')
        item = Expense.objects.get(id=item_id)

        # Retrieve all the form data
        item.item_type = request.POST.get('item_type')
        item.item_name = request.POST.get('item_name')
        item.transaction_option = request.POST.get('transaction_option')
        item.transaction_category = request.POST.get('transaction_category')
        item.internal_option = request.POST.get('internal_option') if item.transaction_category == 'internal' else None
        item.external_type = request.POST.get('external_type') if item.transaction_category == 'external' else None
        item.amount = request.POST.get('amount')
        item.payment_mode = request.POST.get('payment_mode')
        item.voucher_number = request.POST.get('voucher_number') if request.POST.get('transaction_option') == 'voucher' else None
        item.evoucher_number = request.POST.get('evoucher_number')

        # Handle file uploads
        item.bill_photo = request.FILES.get('bill_photo', item.bill_photo)
        item.gst_photo = request.FILES.get('gst_photo', item.gst_photo)
        item.proof_photo = request.FILES.get('proof_photo', item.proof_photo)

        item.save()

        return redirect('item_form')
    
import pytesseract
from pytesseract import Output
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import re
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (20, 30)

# def extract_amount_from_bill(bill_photo_path):
#     # Load the image
#     image = cv2.imread(bill_photo_path)
#     if image is None:
#         raise ValueError("Image could not be loaded. Check the file path.")

#     # Convert to RGB for further processing
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     print("Converted the image to RGB.")

#     # Convert the image to grayscale
#     gray_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

#     # Enhance the image using contrast adjustment
#     # enhancer = ImageEnhance.Contrast(Image.fromarray(gray_image))
#     # enhanced_image = np.array(enhancer.enhance(2))  # Increase contrast
#     # cv2.imshow('enhance',enhanced_image)
#     # print("Enhanced the image contrast.")
    
#     # Apply a simpler global thresholding method instead of adaptive thresholding
#     cv2.imshow('gray',gray_image)
#     _, threshold_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
#     print("Applied Global Thresholding.")



#     # Display the threshold image
#     cv2.imshow(f"Thresholded Image", threshold_image)

#     # Use Tesseract OCR with a different PSM mode (e.g., psm 3 for sparse text)
#     d = pytesseract.image_to_data(threshold_image, config='--psm 7', output_type=Output.DICT)
#     print(d)

#     # Show image with bounding boxes around detected amounts (only for numbers)
#     n_boxes = d['text']
#     img = image.copy()  # Copy the original image to draw bounding boxes

#     for i in range(len(n_boxes)):
#         detected_text = d['text'][i]
#         if int(d['conf'][i]) > 60 and re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)|(\d+(?:,\d{3})*(?:\.\d{1,2})?)', detected_text):  # Check if text matches amount patterns
#             (x, y, w, h) = d["left"][i], d["top"][i], d["width"][i], d["height"][i]
#             img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 200, 0), 1)  # Plot bounding box
#             img = cv2.putText(img, detected_text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)  # Plot text on top of box
#             print(f"Detected amount: {detected_text}")

#     # Show final image with bounding boxes
#     cv2.imshow("Detected Amounts", img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

#     # Process amounts using regex (e.g., ₹ symbols, commas, decimals)
#     amount_pattern = r"₹?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)|(\d+(?:,\d{3})*(?:\.\d{1,2})?)"
#     amounts = re.findall(amount_pattern, ' '.join(d['text']))
#     print(f"Found amounts: {amounts}")

#     # Process total-related amounts (total, sale, amount, etc.)
#     total_pattern = r"(total|fee|net payables|sale|preset|amounttotal|grand\s?total|final\s?total|amount\s?due|net\s?amount|balance|total\s?amount)[^\d]*([\d,]+(?:\.\d{1,2})?)"
#     total_amounts = re.findall(total_pattern, ' '.join(d['text']), re.IGNORECASE)
#     print(f"Found total amounts: {total_amounts}")

#     # Process total amounts first if available
#     if total_amounts:
#         total_amount = max(total_amounts, key=lambda x: float(x[1].replace(",", "")))
#         print(f"Extracted Total Amount: {total_amount[1]}")
#         return total_amount[1]

#     # Process other amounts if no total-related amounts found
#     if amounts:
#         flat_amounts = [amt[0] if amt[0] else amt[1] for amt in amounts]
#         sorted_amounts = sorted(flat_amounts, key=lambda x: float(x.replace(",", "")), reverse=True)
#         print(f"Sorted amounts: {sorted_amounts}")
#         return sorted_amounts[0]

#     print("No amounts found.")
#     return None

# # Example usage
# bill_image_path = '/Users/shashank/XPREDICT/Project/Screenshot 2025-01-11 at 6.06.07 PM.png'  # Path to your bill image
# extracted_amount = extract_amount_from_bill(bill_image_path)
# print(f"Extracted Amount: {extracted_amount}")


# def highlight_amount_in_image(amount_to_highlight, image):
#     """
#     Highlight the detected amount in the image using a bounding box.
#     """
#     try:
#         # Get bounding boxes for all text in the image
#         h, w, _ = image.shape
#         boxes = pytesseract.image_to_boxes(image)

#         # Draw bounding boxes around the amount
#         for box in boxes.splitlines():
#             b = box.split()
#             char = b[0]  # Character recognized
#             x1, y1, x2, y2 = int(b[1]), int(b[2]), int(b[3]), int(b[4])

#             # Match character positions with the amount string
#             if char in amount_to_highlight:
#                 # Scale bounding box to match image dimensions
#                 x1, y1, x2, y2 = int(x1), h - int(y2), int(x2), h - int(y1)
#                 cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

#         # Display the image with highlighted amount
#         cv2.imshow("Highlighted Amount", image)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()

#         return amount_to_highlight

#     except Exception as e:
#         print("Error highlighting amount:", e)
#         return None

# # Example usage
# bill_image_path = '/Users/shashank/XPREDICT/Project/IMG_2954.JPG'
# # extracted_amount = extract_amount_from_bill(bill_image_path)
# # print(f"Extracted Amount: {extracted_amount}")

def preprocess_image(image):
    """
    Preprocess the image to improve OCR accuracy.
    - Apply thresholding.
    - Perform morphological operations to fill discontinuities.
    - Optionally apply Gaussian blur for smoothing.
    """
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray",gray)
    # cv2.waitKey(0)

    # Apply binary thresholding
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Use morphological operations to fill font discontinuities
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # Rectangular kernel

    dilated = cv2.dilate(binary, kernel, iterations=1)  # Dilation to fill gaps

    processed = cv2.erode(dilated, kernel, iterations=1)  # Erosion to refine text


    # Apply Gaussian blur for smoothing (optional)
    smoothed = cv2.GaussianBlur(processed, (3, 3), 0)


    return smoothed

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import cv2
import numpy as np

def extract_amount_from_bill(bill_photo_path):
    print(f"bill_photo_path",bill_photo_path)
    try:
        # Read the image using OpenCV
        
        image = cv2.imread(bill_photo_path)
        if image is None:
            raise ValueError("Image could not be loaded. Check the file path.")
        # cv2.imshow("og",image)
        # cv2.waitKey(0)

        # Upscale the original image
        scale_factor = 2  # Increase resolution by 2x
        upscaled_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
        # cv2.imshow("up image",upscaled_image)
        # cv2.waitKey(0)  # Wait for a key press to close the window
        # cv2.destroyAllWindows()

        # Convert the image to HSV and detect yellow highlights
        image_hsv = cv2.cvtColor(upscaled_image, cv2.COLOR_BGR2HSV)
        hsv_min = np.array([20, 50, 50])
        hsv_max = np.array([35, 255, 255])
        mask = cv2.inRange(image_hsv, hsv_min, hsv_max)
        highlighted_image = cv2.bitwise_and(upscaled_image, upscaled_image, mask=mask)
        # cv2.imshow("highlighted image", highlighted_image)

        # Convert highlighted image to grayscale
        highlighted_gray = cv2.cvtColor(highlighted_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(highlighted_gray, 140, 255, cv2.THRESH_BINARY)

        # Find contours to locate the largest bounding box
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_bbox = max(contours, key=cv2.contourArea, default=None)

        if largest_bbox is not None:
            x, y, w, h = cv2.boundingRect(largest_bbox)
            cropped_image = upscaled_image[y:y+h, x:x+w]

            # Preprocess the cropped image
            preprocessed_image = preprocess_image(cropped_image)
            # cv2.imshow("Preprocessed Image", preprocessed_image)
            # cv2.waitKey(0)  # Wait for a key press to close the window
            # cv2.destroyAllWindows()

            # Perform OCR on the preprocessed image
            text = pytesseract.image_to_string(preprocessed_image, config='--psm 6')
            print("Extracted Text:", text)

            # Use regex to extract amounts
            amount_pattern = r"₹?(\d{1,5}(?:,\d{3})*(?:\.\d{1,2})?)"
            amounts = re.findall(amount_pattern, text)
            print("Found amounts:", amounts)
            print(f"final amount",amounts[0])
            return amounts[0] if amounts else None
            
        else:
            print("No text regions found.")
            return None

    except Exception as e:
        print("Error extracting amount:", e)
        return None

def ocr_func(image_p):
    # cv2.imshow("sdjhgjwbcerf",image_p)
    # cv2.waitKey(0)
    # image = cv2.imread(image_p)
    # gray_image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)

    # cv2.imshow('gray',gray_image)
    # _, threshold_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
#     print("Applied Global Thresholding.")



#     # Display the threshold image
    # cv2.imshow(f"Thresholded Image", threshold_image)

#     # Use Tesseract OCR with a different PSM mode (e.g., psm 3 for sparse text)
    d = pytesseract.image_to_data(image_p, config='--psm 7', output_type=Output.DICT)
    print(d)

#     # Show image with bounding boxes around detected amounts (only for numbers)
    n_boxes = d['text']
    img = image_p.copy()  # Copy the original image to draw bounding boxes

    for i in range(len(n_boxes)):
        detected_text = d['text'][i]
        if int(d['conf'][i]) > 60 and re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)|(\d+(?:,\d{3})*(?:\.\d{1,2})?)', detected_text):  # Check if text matches amount patterns
            (x, y, w, h) = d["left"][i], d["top"][i], d["width"][i], d["height"][i]
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 200, 0), 1)  # Plot bounding box
            img = cv2.putText(img, detected_text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)  # Plot text on top of box
            print(f"Detected amount: {detected_text}")

#     # Show final image with bounding boxes
        cv2.imshow("Detected Amounts", img)
        cv2.waitKey(0)
#     cv2.waitKey(0)




# def highlight_amount_in_image(amount_to_highlight, image):
#     """
#     Highlight the detected amount in the image using a bounding box.
#     """
#     try:
#         # Get bounding boxes for all text in the image
#         h, w, _ = image.shape
#         boxes = pytesseract.image_to_boxes(image)

#         # Draw bounding boxes around the amount
#         for box in boxes.splitlines():
#             b = box.split()
#             char = b[0]  # Character recognized
#             x1, y1, x2, y2 = int(b[1]), int(b[2]), int(b[3]), int(b[4])

#             # Match character positions with the amount string
#             if char in amount_to_highlight:
#                 # Scale bounding box to match image dimensions
#                 x1, y1, x2, y2 = int(x1), h - int(y2), int(x2), h - int(y1)
#                 cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

#         # Display the image with highlighted amount
#         # cv2.imshow("Highlighted Amount", image)

#         cv2.waitKey(0)

#         return amount_to_highlight

#     except Exception as e:
#         print("Error highlighting amount:", e)
#         return None

# # Example usage
# bill_image_path = '/Users/shashank/XPREDICT/Project/M3.jpeg'
# extracted_amount = extract_amount_from_bill(bill_image_path)
# print(f"Extracted Amount: {extracted_amount}")  

import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt  # Ensure CSRF is handled for AJAX requests
def process_uploaded_photo(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name  # Get the temp file path

        try:
            # Extract amount from the uploaded file
            extracted_amount = extract_amount_from_bill(temp_file_path)
            print(temp_file_path)
            
        except Exception as e:
            extracted_amount = None
            print(f"Error during OCR processing: {e}")
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)

        # Return the extracted amount or error
        if extracted_amount:
            return JsonResponse({'success': True, 'amount': extracted_amount})
        else:
            return JsonResponse({'success': False, 'message': 'Amount could not be extracted. Please try again.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import logging
from django.core.files.storage import default_storage

# Log setup (Optional for debugging)
logger = logging.getLogger(__name__)

@csrf_exempt  # Temporarily disable CSRF validation for testing
def process_photo(request):
    if request.method == 'POST' and request.FILES.get('file'):
        print(f"uploaded file",request.POST)
        uploaded_file = request.FILES['file']
        

        # Save the file to the MEDIA_ROOT directory
        file_name = uploaded_file.name
        file_full_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Save the uploaded file using Django's default file storage
        try:
            with default_storage.open(file_full_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            # Call a function to extract the amount from the bill photo
            extracted_amount = extract_amount_from_bill(file_full_path)

            if extracted_amount:
                # Return the amount extracted from the bill
                return JsonResponse({'success': True, 'amount': extracted_amount})
            else:
                # If the extraction failed, send an error message
                return JsonResponse({'success': False, 'error': 'Failed to extract amount from the bill.'})

        except Exception as e:
            logger.error(f"Error processing photo: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Error processing the file.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

def upload_temporary(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage(location='media/tmp/')  # Specify a temporary folder
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)
        
        return JsonResponse({'success': True, 'file_url': file_url})

    return JsonResponse({'success': False, 'message': 'No file uploaded.'})


import pytesseract
from django.http import JsonResponse
import cv2
import numpy as np
from django.views.decorators.csrf import csrf_exempt

# Set the Tesseract OCR executable path
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

# @csrf_exempt
# def process_bill_photo(request):
#     print(f"post data")
#     if request.method == 'POST' and request.FILES.get('bill_photo'):
#         print(f"post data",request.POST)
#         file = request.FILES['bill_photo']

#         image_data = file.read()
#         np_array = np.frombuffer(image_data, np.uint8)
#         opencv_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

#         if opencv_image is None:
#             return JsonResponse({'error': 'Unable to decode the image.'})

#         extracted_text = pytesseract.image_to_string(opencv_image)
#         amount = None
#         for line in extracted_text.splitlines():
#             if 'Amount' in line:
#                 parts = line.split()
#                 for part in parts:
#                     try:
#                         amount = float(part.replace(',', '').replace('₹', '').strip())
#                         break
#                     except ValueError:
#                         continue

#         if amount:
#             return JsonResponse({'amount': amount})
#         else:
#             return JsonResponse({'error': 'Amount not found in the image.'})

#     return JsonResponse({'error': 'Invalid request.'})

    
from .models import Expense, CashVoucher, User, BorrowedAmount, ProofPhoto
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, datetime
import decimal
from decimal import Decimal, InvalidOperation
from django.shortcuts import redirect
from django.contrib import messages
from website.models import CashVoucher

def new_item_form(request, user_id):
    current_date = date.today()
    selected_user = get_object_or_404(User, id=user_id)
    is_draft = False  # Initialize is_draft for all request methods
    total_amount = 0  # Initialize total_amount for all request methods
    transaction_category = ""
    conveyance_options = Conveyance.objects.all()
    
    if request.method == "POST":
        print(f"post",request.POST)


        item_type = request.POST.get("item_type")
        item_names = request.POST.getlist('item_name', [])
        item_name = next((name for name in item_names if name.strip()), None)
        transaction_option = request.POST.get("transaction_option")
        print(transaction_option)
        transaction_category = request.POST.get("transaction_category")
        kilometers = request.POST.get("kilometers")  # New field
        print(f"Kilometers received: {kilometers}")
        vehicle_type = request.POST.get("vehicle_type") 
        internal_options = request.POST.getlist("internal_option")
        external_type = request.POST.get("external_type")
        total_amount = request.POST.get("amount", "").replace(",", "").strip()
        print(f"ttamt",total_amount)


        
        payment_mode = request.POST.get("payment_mode")
        voucher_number = request.POST.get("voucher_number")
        evoucher_number = request.POST.get("e_voucher_number")
        transaction_dates = request.POST.getlist('transaction_date', [])
        transaction_date = next(
                (datetime.strptime(date.strip(), "%Y-%m-%d").date() for date in transaction_dates if date.strip()),
                None,
            )
        bill_photo = request.FILES.get("bill_photo")
        if bill_photo:
                print("Bill photo uploaded:", bill_photo.name)  # Print the name of the uploaded file
                amount = extract_amount_from_bill(bill_photo)
                if amount is not None:
                    print(f"Extracted bill Amount: {amount}")
                    total_amount = amount  # Override total_amount with extracted value
                    print(f"ttmount",total_amount)
                else:
                    messages.error(request, "No amount found in the bill.")
        else:
                messages.error(request, "No bill photo uploaded.")
                print("No bill photo uploaded.")

        gst_photo = request.FILES.get("gst_photo")
        if gst_photo:
                print("GST photo uploaded:", gst_photo.name)  # Print the name of the uploaded file
                amount = extract_amount_from_bill(gst_photo)
                if amount is not None:
                    print(f"Extracted Amount: {amount}")
                    total_amount = amount  # Override total_amount with extracted value
                else:
                    messages.error(request, "No amount found in the bill.")
        else:
                messages.error(request, "No bill gst photo uploaded.")
        proof_files = request.FILES.getlist("proof_photos")
        if transaction_option in ["2_wheeler", "4_wheeler"] and kilometers:
            print(f"Kilometers provided: {kilometers}")

            try:
                # Try to convert kilometers to float and log the conversion
                kilometers = Decimal(kilometers)
                print(f"Kilometers converted to float: {kilometers}")
            
                
                # Fetch conveyance information based on vehicle_type
                print(f"toption",transaction_option)
                vehicle_type = transaction_option
                print(f"vhtype",vehicle_type)
                conveyance = Conveyance.objects.filter(vehicle_type=vehicle_type).first()
                print(f"Conveyance fetched: {conveyance}")
                
                if conveyance:
                    # Calculate total_amount if conveyance exists
                    print(f"if convey",total_amount)
                    total_amount = kilometers * conveyance.price_per_km
                    print(f"Calculated amount for {vehicle_type}: {total_amount}")
                else:
                    # If no conveyance found, show an error
                    messages.error(request, f"No conveyance rate found for {vehicle_type}.")
                    total_amount = 0

            except ValueError:
                # If conversion fails, show an error and reset total_amount to 0
                messages.error(request, "Invalid kilometers value.")
                total_amount = 0
                print("Error: Invalid kilometers value. Setting total_amount to 0.")
        
            # File uploads
            
        # Check if 'draft_status' is in the POST data and set is_draft accordingly

        draft_statuss = request.POST.get('draft_status') 
        print(f"defmain",draft_statuss) # Default to 'false' if not provided
        draft_status = request.POST.get('draft_status', 'false')  # Default to 'false' if not provided
        print(f"def",draft_status)
        is_draft = draft_status.lower() == 'true'  # Set is_draft to True if 'draft_status' is 'true', otherwise False
        print(f"before storing to model",total_amount)

        # Save the primary expense for User 1
        expense = Expense.objects.create(
            
            created_by=request.user,
            item_type=item_type,
            item_name=item_name,
            transaction_option=transaction_option,

            transaction_category=transaction_category,
            internal_option=",".join(internal_options) if transaction_category == "internal" else None,
            external_type=external_type if transaction_category == "external" else None,
            
            payment_mode=payment_mode,
            voucher_number=voucher_number if transaction_option == "voucher" else None,
            evoucher_number=evoucher_number,
            bill_photo=bill_photo,
            gst_photo=gst_photo,
            
            transaction_date=transaction_date,
            is_draft=is_draft,  # Set the is_draft field based on the form submission
            amount=total_amount,
        )
        for file in proof_files:
            if file:
                ProofPhoto.objects.create(expense=expense, file=file)

        print(f"after context",transaction_option)

        print(f"isdraft",is_draft)
        # Handle borrowed amounts and replicate vouchers for multiple borrowed users
                # Handle borrowed amounts and replicate vouchers for multiple borrowed users
        borrowed_amounts = request.POST.getlist("borrowed_amounts[]")
        borrowed_froms = request.POST.getlist("borrowed_froms[]")

        # Initialize remaining amount
        remaining_amount = decimal.Decimal(total_amount)

        for borrowed_amount, borrowed_from in zip(borrowed_amounts, borrowed_froms):
            if borrowed_amount and borrowed_from:
                borrowed_amount = decimal.Decimal(borrowed_amount)  # Convert borrowed amount to Decimal

                if borrowed_amount <= remaining_amount:
                    # Create a BorrowedAmount entry
                    BorrowedAmount.objects.create(
                        expense=expense,
                        amount=borrowed_amount,
                        borrowed_from_id=borrowed_from,
                    )

                    # Replicate the voucher for the borrowed user (User 2, User 3, etc.)
                    Expense.objects.create(
                        created_by=User.objects.get(id=borrowed_from),
                        item_type=item_type,
                        item_name=f"Borrowed - {item_name}",
                        transaction_option=None,
                        internal_option=request.user,
                        transaction_category="internal",
                        amount=borrowed_amount,  # Assign borrowed amount
                        payment_mode=payment_mode,
                        voucher_number=voucher_number if transaction_option == "voucher" else None,
                        evoucher_number=evoucher_number,
                        bill_photo=None,
                        gst_photo=None,
                        proof_photo=None,
                        transaction_date=transaction_date,
                    )

                    # Reduce the remaining amount
                    remaining_amount -= borrowed_amount
                else:
                    continue  # Skip if borrowed amount exceeds available funds

        # Ensure User 1’s expense is updated with the correct remaining amount
        expense.amount = remaining_amount  # Should be 0 if fully borrowed
        expense.save()


        # Initialize cvamount before the block
        cvamount = 0

        if transaction_category == "external":
            cvamount = request.POST.get('cvamount', '').strip()
            if cvamount:
                    try:
                        cvamount = decimal.Decimal(cvamount)
                    except decimal.InvalidOperation:
                        cvamount = 0  # Handle invalid decimals gracefully
            else:
                    cvamount = 0

            
            

        if "tips_checkbox" in request.POST:
            is_tips_selected = request.POST.get("tips_checkbox") == "on"

            if is_tips_selected:
        # Fetch the Cash Voucher details from the form
                cv_amount = request.POST.get("cvamount", "").strip()
                paid_to = request.POST.get("paid_to", "").strip()
                cv_item_name = request.POST.get("item_name", "").strip()
                cv_transaction_date = request.POST.get("transaction_date", "").strip()
                cv_voucher_number = request.POST.get("tip_voucher_number", "")

                # Validate all required fields
                if not (cv_amount and paid_to and cv_item_name and cv_transaction_date):
                    messages.error(request, "All Cash Voucher fields are required.")
                    return redirect("item_form")

                # Validate and convert cv_amount to Decimal
                try:
                    cv_amount = Decimal(cv_amount)
                except InvalidOperation:
                    messages.error(request, "Invalid Cash Voucher amount.")
                    return redirect("item_form")

                # Create the Cash Voucher with 'pending' status
                cash_voucher = CashVoucher.objects.create(
                    created_by=request.user,
                    amount=cv_amount,
                    paid_to=paid_to,
                    item_name=cv_item_name,
                    transaction_date=cv_transaction_date,
                    voucher_number=cv_voucher_number,
                    status="pending",  # Set status to 'pending'
                    expense=expense,
                )
                messages.success(request, "Cash Voucher saved successfully! Awaiting approval.")

                # Link Cash Voucher amount to the E-Voucher only if voucher is approved
                evoucher_number = request.POST.get("e_voucher_number", "").strip()
                if evoucher_number:
                    try:
                        # Find the corresponding Expense with the given eVoucher number
                        evoucher_expense = Expense.objects.get(evoucher_number=evoucher_number)

                        # Only update the amount if the cash voucher is approved
                        if cash_voucher.status == 'approved':
                            evoucher_expense.amount += cv_amount
                            evoucher_expense.save()
                            messages.success(request, "Cash Voucher amount added to E-Voucher successfully!")
                        else:
                            messages.error(request, "Cash Voucher is not approved yet. Cannot update the E-Voucher amount.")
                    except Expense.DoesNotExist:
                        messages.error(request, f"No Expense found with E-Voucher number {evoucher_number}.")
                else:
                    messages.error(request, "E-Voucher number is required to link the Cash Voucher.")
            else:
                messages.error(request, "Please complete all required Cash Voucher fields.")

        # Redirect back to the draft page or same form to review the draft data
        if is_draft:
            return redirect("draft_vouchers")  # Redirect to the draft vouchers list page
        return redirect("item_form")  # Ensure 'item_form' is a valid URL pattern name

    # Fetch approved vouchers for the selected user
    used_voucher_numbers = list(Expense.objects.values_list("voucher_number", flat=True).exclude(voucher_number__isnull=True).distinct())
    approved_vouchers = CashVoucher.objects.filter(
        created_by=selected_user, status="approved"
    ).exclude(voucher_number__in=used_voucher_numbers)
    users = User.objects.all()

    evoucher_number = generate_evoucher_number()
    submitted_data = request.POST or None
    cv_voucher_number =generate_voucher_number()

    context = {
        "approved_vouchers": approved_vouchers,
        "evoucher_number": evoucher_number,
        "current_date": current_date,
        "selected_user": selected_user,
        "users": users,
        'conveyance_options': conveyance_options,
        'submitted_data': submitted_data,
        'cv_voucher_number':cv_voucher_number,
        
    }

    return render(request, "xp/newitemform.html", context)




from .models import Expense
from django.shortcuts import render

def draft_vouchers(request):
    # Retrieve all draft vouchers
    draft_vouchers = Expense.objects.filter(is_draft=True)

    context = {
        "expenses": draft_vouchers
    }

    return render(request, "xp/draft_vouchers.html", context)




from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .models import CashVoucher, User
from django.db.models import Q
from django.utils.dateparse import parse_date

def cash_voucher(request):
    approved_vouchers = CashVoucher.objects.filter(status='approved').order_by('-id')
    rejected_vouchers = CashVoucher.objects.filter(status='rejected').order_by('-id')
    total_amount = sum(voucher.amount for voucher in approved_vouchers)

    # Get the current date
    current_date = datetime.today().date()

    # Default queryset for vouchers
    cash_vouchers = CashVoucher.objects.all().order_by('-id')

    # Check if the user is admin or superuser
    if not (request.user.is_staff or request.user.is_superuser):
        # Regular users can only see their own vouchers
        cash_vouchers = CashVoucher.objects.filter(created_by=request.user).order_by('-id')

    # User filter logic (from payable view)
    selected_user = None
    user_id = request.GET.get('user_id')  # Get the selected user from the GET request
    if user_id:
        selected_user = User.objects.get(id=user_id)
        cash_vouchers = cash_vouchers.filter(created_by=selected_user)

    # Get the search query and date filters from GET parameters
    search_query = request.GET.get('q', '')
    date_from = request.GET.get('transaction_date_from', '')
    date_to = request.GET.get('transaction_date_to', '')

    # Apply search query filter if it exists
    if search_query:
        cash_vouchers = cash_vouchers.filter(
            Q(voucher_number__icontains=search_query) |
            Q(paid_to__icontains=search_query) |
            Q(item_name__icontains=search_query) |
            Q(amount__icontains=search_query) |
            Q(status__icontains=search_query)
        )

    # Apply date filters if they exist
    if date_from:
        parsed_date_from = parse_date(date_from)
        if parsed_date_from:
            cash_vouchers = cash_vouchers.filter(transaction_date__gte=parsed_date_from)

    if date_to:
        parsed_date_to = parse_date(date_to)
        if parsed_date_to:
            cash_vouchers = cash_vouchers.filter(transaction_date__lte=parsed_date_to)

    # Handle voucher approval
    verify_id = request.GET.get('verify_id')
    if verify_id:
        try:
            voucher = get_object_or_404(CashVoucher, id=verify_id)
            if voucher.status == 'pending':
                voucher.status = 'approved'
                voucher.approved_by = request.user.username 
                voucher.verified_at = timezone.now()  # Track who approved
                voucher.save()

                # Create a notification for the user who created the voucher
            Notification.objects.create(
                    user=voucher.created_by,
                    title=f"Your Cash Voucher has been approved",
                    message=f"Your voucher with number {voucher.voucher_number} of amount  {voucher.amount} has been approved."
                )
        except Exception as e:
            print(f"Error while verifying voucher: {e}")

    # Handle voucher rejection
    reject_id = request.GET.get('reject_id')
    if reject_id:
        try:
            voucher = get_object_or_404(CashVoucher, id=reject_id)
            if voucher.status == 'pending':  # Only allow rejection of pending vouchers
                voucher.status = 'rejected'
                voucher.approved_by = request.user.username
                voucher.save()

                # Create a notification for the user who created the voucher
            Notification.objects.create(
                    user=voucher.created_by,
                    title=f"{CashVoucher.voucher_number} of amount {CashVoucher.amount} is rejected",
                    message=f"Your voucher with number {CashVoucher.voucher_number} has been rejected."
                )
        except Exception as e:
            print(f"Error while rejecting voucher: {e}")


    # Pass the current date, vouchers, and search query to the template
    return render(request, 'xp/cash_voucher.html', {
        'current_date': current_date,
        'vouchers': cash_vouchers,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'approved_vouchers': approved_vouchers,
        'rejected_vouchers': rejected_vouchers,
        'total_amount': total_amount,
        'selected_user': selected_user,
        'users': User.objects.all(),  # List of all users for the filter

    })

from django.db.models import Sum

def approved_vouchers(request):
    user = request.user
    
    # If the user is admin, fetch all approved vouchers
    if user.is_staff or user.is_superuser:
        vouchers = CashVoucher.objects.filter(status='approved').order_by('-id')
    else:
        # If not an admin, fetch only the approved vouchers created by the user
        vouchers = CashVoucher.objects.filter(created_by=user, status='approved').order_by('-id')

    # Debug print to check the result of the query


    # Calculate the total amount of the approved vouchers
    total_amount = vouchers.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    # Prepare context with vouchers and total amount
    context = {'vouchers': vouchers, 'total_amount': total_amount}

    return render(request, 'xp/approved_vouchers.html', context)

def rejected_vouchers(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        rejected_vouchers = CashVoucher.objects.filter(status='rejected')
    else:
         rejected_vouchers = CashVoucher.objects.filter(created_by=user, status='rejected')

    context = {'rejected_vouchers': rejected_vouchers}
    return render(request, 'xp/rejected_vouchers.html', context)


def cash_voucher_success(request):
    return render(request, 'xp/success.html')

from django.shortcuts import render, redirect
from .forms import CashVoucherForm
from .models import CashVoucher

def create_cash_voucher(request):
    current_date = datetime.today().date()
    if request.method == 'POST':
        form = CashVoucherForm(request.POST)

        if form.is_valid():
            transaction_date = form.cleaned_data.get('transaction_date')
            form.save()  # Saves the cash voucher in the database
            return redirect('success')  # Redirect to a success page or another view
    else:
        form = CashVoucherForm()
    
    return render(request, 'xp/create_cash_voucher.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import CashVoucher

def reject_voucher(request):
    if request.method == 'POST':
        voucher_id = request.POST.get('voucher_id')
        rejection_reason = request.POST.get('reason')

        # Ensure voucher exists
        voucher = get_object_or_404(CashVoucher, id=voucher_id)

        # Only reject vouchers that are pending
        if voucher.status == 'pending':
            voucher.status = 'rejected'
            voucher.rejection_reason = rejection_reason  # Assuming you have a 'rejection_reason' field

            voucher.save()

            # Show a success message
            messages.success(request, 'Voucher rejected successfully!')
        else:
            messages.error(request, 'Voucher cannot be rejected at this stage.')

        return redirect('rejected_vouchers')  # Redirect to the page with the vouchers

from django.shortcuts import render, get_object_or_404, redirect
from .models import CashVoucher


def approve_cash_voucher(request, voucher_number):
    # Check if user has permission to approve
    if not request.user.has_perm('app.can_approve'):
        return redirect('permission_denied')  # Redirect to permission denied page if no permission
    
    # Get the voucher by voucher number
    voucher = get_object_or_404(CashVoucher, voucher_number=voucher_number)

    # If voucher status is already approved, prevent re-approval
    if voucher.status == 'approved':
        return redirect('voucher_already_approved')  # Redirect to a page showing it's already approved

    # Approve the voucher
    voucher.status = 'approved'
    voucher.approved_by = request.user.username  # Set the approver as the current user
    voucher.save()

    return redirect('approval_success')  # Redirect to a success page after approval



def e_voucher(request):
    # Fetch only approved vouchers
    approved_vouchers = CashVoucher.objects.filter(status='approved')
    
    if request.method == 'POST':
        # Handle form submission
        voucher_number = request.POST.get('voucher_number')
        # Use the selected voucher number for processing
        # ...

    return render(request, 'xp/e_voucher_page.html', {
        'approved_vouchers': approved_vouchers,
    })







from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CashVoucher
from datetime import datetime

# This function will generate the voucher number
def generate_voucher_number():
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
    
    return voucher_number


# from django.shortcuts import render, redirect
# from .models import Voucher
# from .forms import VoucherForm

# def voucher_view(request):
#     if request.method == 'POST':
#         form = VoucherForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('voucher_view')  # Redirect to the same page to display updated data
#     else:
#         form = VoucherForm()

#     # Fetch all vouchers (latest first)
#     vouchers = Voucher.objects.all().order_by('-voucher_number')
#     return render(request, 'xp/voucher_page.html', {'form': form, 'vouchers': vouchers})


from django.shortcuts import render
from .models import Expense

def e_voucher_page(request):
    """
    View to display all submitted expenses (e-vouchers).
    """
    # Fetch all Expense records, ordered by the most recent submission
    expenses = Expense.objects.all().order_by('-id')  # Assuming you have a 'created_at' timestamp field

    context = {
        'expenses': expenses,
    }

    return render(request, 'xp/e_voucher_page.html', context)


from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.db.models import ForeignKey

def expense_form(request):
    # Retrieve search query from request
    search_query = request.GET.get('search', '')

    # Base queryset for all expenses
    expenses = Expense.objects.all()

    if search_query:
        # Initialize a Q object for global search
        global_filter = Q()

        # Loop through all fields of the Expense model
        for field in Expense._meta.fields:
            field_name = field.name

            if isinstance(field, ForeignKey):
                # Handle ForeignKey fields (searching related fields)
                related_model = field.related_model
                related_fields = [f.name for f in related_model._meta.fields if f.name != 'id']
                for related_field in related_fields:
                    global_filter |= Q(**{f"{field_name}__{related_field}__icontains": search_query})

            elif field.choices:  # Handle choice fields
                for value, display in dict(field.choices).items():
                    if search_query.lower() in display.lower():
                        global_filter |= Q(**{f"{field_name}": value})

            else:
                # Handle regular fields with icontains
                global_filter |= Q(**{f"{field_name}__icontains": search_query})

        # Filter expenses using the global_filter
        expenses = expenses.filter(global_filter)

    # Apply ordering and pagination
    expenses = expenses.order_by('-id')
    paginator = Paginator(expenses, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add sequence numbers for the paginated records
    start_sequence_number = (page_obj.number - 1) * paginator.per_page + 1
    for index, expense in enumerate(page_obj, start=start_sequence_number):
        expense.sequence_number = index

    # Prepare the form for adding new expenses
    form = ExpenseForm()

    # Render the template with search results and form
    return render(request, 'xp/item_form.html', {
        'form': form,
        'page_obj': page_obj,
        'search_query': search_query,
    })
    

def expense_details(request, expense_id):
    """
    View to show the details of a specific expense.
    """
    expense = get_object_or_404(Expense, id=expense_id)
    context = {
        'expense': expense
    }
    return render(request, 'xp/expense_details.html', context)


# from django.shortcuts import render
# # from .forms import ItemForm
# from .models import Voucher

# def new_e_voucher(request):
#     # Handle form submission
#     if request.method == "POST":
#         form = ExpenseForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()  # Save the form data to the database
#     else:
#         form = ExpenseForm()

#     # Retrieve all vouchers after form submission (including newly saved ones)
#     vouchers = Voucher.objects.all()  # Fetch all voucher data from the database

#     # Pass the form and vouchers data to the template
#     return render(request, 'xp/item_form.html', {'form': form, 'vouchers': vouchers})




from django.shortcuts import render, redirect
from .forms import ExpenseForm  # Or use ItemForm, if it's the form you're referring to
from .models import Expense

def expense_home(request):
    # Retrieve all Expense records
    expenses = Expense.objects.all()

    # If the form is submitted, handle it here
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the new expense record
            return redirect('expense_home')  # Redirect back to this page after saving
    else:
        form = ExpenseForm()

    # Render the page with the form and all expenses
    return render(request, 'xp/expense_home.html', {
        'form': form,
        'expenses': expenses
    })

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import CashVoucher
from datetime import date

def new_cash_voucher_form(request):
    current_date = date.today()

    if request.method == 'POST':
        voucher_number = request.POST.get('voucher_number')
        cvamount = request.POST.get('cvamount')
        paid_to = request.POST.get('paid_to')
        item_name = request.POST.get('item_name')
        transaction_date = request.POST.get('transaction_date') 
        proof_photo = request.FILES.get('proof_photo')



        # Validate required fields
        if not cvamount or not paid_to or not item_name:

            return render(request, 'xp/new_cash_voucher_form.html', {'current_date': current_date },'voucher_number')

        try:
            # Create a new CashVoucher instance
            new_voucher = CashVoucher.objects.create(
                created_by=request.user,
                voucher_number=voucher_number,
                amount=cvamount,
                paid_to=paid_to,
                item_name=item_name,
                transaction_date=transaction_date,
                proof_photo=proof_photo,

            )


            return redirect('cash_voucher')  # Redirect back to the form page

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('new_cash_voucher_form')

    # GET request: fetch all existing vouchers
    cash_vouchers = CashVoucher.objects.all()
    cv_voucher_number =generate_voucher_number()
    context = {
        'current_date': current_date,
        'cash_vouchers': cash_vouchers,  # Pass the list of vouchers
        'cv_voucher_number':cv_voucher_number,
    }

    return render(request, 'xp/new_cash_voucher_form.html', context)

def edit_item(request, item_id):
    expense = get_object_or_404(Expense, id=item_id)
    users = User.objects.all()
    used_voucher_numbers = list(
        Expense.objects.values_list("voucher_number", flat=True)
        .exclude(voucher_number__isnull=True)
        .distinct()
    )
    approved_vouchers = CashVoucher.objects.filter(
        created_by=expense.created_by, status="approved"
    ).exclude(voucher_number__in=used_voucher_numbers)
    

    if request.method == "POST":
        item_type = request.POST.get('item_type')
        item_name = request.POST.get('item_name')
        transaction_option = request.POST.get('transaction_option')
        payment_category = request.POST.get('payment_category')
        transaction_category = request.POST.get('transaction_category')
        internal_option = request.POST.get('internal_option')
        external_type = request.POST.get('external_type')
        amount = request.POST.get('amount')
        payment_mode = request.POST.get('payment_mode')
        transaction_date = request.POST.get('transaction_date')
        voucher_number = request.POST.get("voucher_number")
        evoucher_number = request.POST.get('e_voucher_number')
        proof_files = request.FILES.getlist("proof_photos")
        borrowed_amounts = request.POST.getlist("borrowed_amounts[]")
        borrowed_froms = request.POST.getlist("borrowed_froms[]")
        draft_status = request.POST.get('draft_status', 'false')
        if voucher_number:
            try:
                voucher = CashVoucher.objects.get(voucher_number=voucher_number)
                expense.amount = voucher.amount  # override with voucher amount
                expense.voucher_number = voucher.voucher_number  # link voucher to expense
                voucher.expense = expense  # if you are tracking this reverse relation
                voucher.save()
            except CashVoucher.DoesNotExist:
                pass
        else:
            # No voucher selected, use manually entered amount
            expense.amount = request.POST.get('amount')
        

        is_draft = draft_status.lower() == 'true'
        # Handle photo updates
        if 'remove_bill_photo' in request.POST:
            if expense.bill_photo:
                expense.bill_photo.delete()
            expense.bill_photo = None
        else:
            if 'bill_photo' in request.FILES:
                expense.bill_photo = request.FILES['bill_photo']

        if 'remove_gst_photo' in request.POST:
            if expense.gst_photo:
                expense.gst_photo.delete()
            expense.gst_photo = None
        else:
            if 'gst_photo' in request.FILES:
                expense.gst_photo = request.FILES['gst_photo']

        # Validate amount
        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'message': 'Invalid amount value.'})
        for file in proof_files:
            if file:
                ProofPhoto.objects.create(expense=expense, file=file)

        # Update expense fields
        expense.item_type = item_type
        expense.voucher_number=voucher_number
        expense.item_name = item_name
        expense.payment_category = payment_category
        expense.transaction_category = transaction_category
        expense.amount = amount  # This will be updated later if there's borrowed portion
        expense.payment_mode = payment_mode
        expense.transaction_date = transaction_date
        expense.evoucher_number = evoucher_number
        expense.internal_option = internal_option
        expense.external_type = external_type   
        expense.is_draft = is_draft
        expense.transaction_option = transaction_option

       

        expense.save()  # Save updated data before processing borrowed amounts
       

        # Clear existing borrowed records


        # Handle borrowed amounts
        borrowed_froms_filtered = [id for id in borrowed_froms if id.strip()]
        remaining_amount = amount
        borrowed_amount_objects = []

        for borrowed_amount, borrowed_from in zip(borrowed_amounts, borrowed_froms_filtered):
            if borrowed_amount and borrowed_from:
                borrowed_amount = Decimal(borrowed_amount)
                user = User.objects.get(id=borrowed_from)

                if borrowed_amount <= remaining_amount:
                    borrowed_amount_objects.append(
                        BorrowedAmount(
                            expense=expense,
                            borrowed_from=user,
                            amount=borrowed_amount
                        )
                    )

                    Expense.objects.create(
                        created_by=user,
                        item_type=item_type,
                        item_name=f"Borrowed - {item_name}",
                        transaction_option='voucher',
                        transaction_category="internal",
                        amount=borrowed_amount,
                        payment_mode=payment_mode,
                        voucher_number=expense.voucher_number,
                        evoucher_number=evoucher_number,
                        proof_photo=None,
                        transaction_date=transaction_date,
                        is_draft=is_draft,
                        status="pending"  # Add status if required by model
                    )

                    remaining_amount -= borrowed_amount

        BorrowedAmount.objects.bulk_create(borrowed_amount_objects)
        

        # Update expense with remaining amount (if any)
        if remaining_amount > 0:
            expense.amount = remaining_amount
            expense.save()

        # Redirect based on draft status
        return redirect("draft_vouchers" if is_draft else "item_form")

    # GET request
    return render(request, 'xp/edit_item.html', {
        "approved_vouchers": approved_vouchers,
        'expense': expense,
        'evoucher_number': expense.evoucher_number,
        'users': users,
        'submitted_data': {'internal_option': expense.internal_option},

    })


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import CashVoucher  # Replace with your model name

def get_voucher_data(request):
    if request.method == "GET" and request.GET.get("id"):
        voucher_id = request.GET.get("id")
        voucher = get_object_or_404(CashVoucher, id=voucher_id)  # Fetch the voucher
        # Prepare data to return as JSON (voucher_id is not included)
        data = {
            "voucher_number": voucher.voucher_number,
            "amount": voucher.amount,
            "paid_to": voucher.paid_to,
            "item_name": voucher.item_name,
            "transaction_date": voucher.transaction_date,
        }
        return JsonResponse(data)  # Return the data in JSON format

from django.shortcuts import render, get_object_or_404, redirect
from .models import CashVoucher 
from .forms import CashVoucherForm  # Replace with your actual form class

from django.shortcuts import render, get_object_or_404, redirect
from .forms import CashVoucherForm
from .models import CashVoucher

def edit_cash_voucher_form(request, voucher_id):
    voucher = get_object_or_404(CashVoucher, id=voucher_id)  # Fetch the voucher

    if request.method == 'POST':
        # Bind the form with the POST data and the instance to be updated
        form = CashVoucherForm(request.POST, instance=voucher)
        
        # Debugging: Print POST data and form validity

        
        if form.is_valid():  # Validate the form

            form.save()  # Save the changes to the database
            return redirect('cash_voucher')  # Redirect after saving
        else:
            # Debugging: Print form errors if not valid
            print("Form errors:", form.errors)

    else:
        # If GET, display the form with current data

        form = CashVoucherForm(instance=voucher)

    return render(request, 'xp/edit_cash_voucher.html', {'form': form, 'voucher': voucher})



def save_expense(request):
    if request.method == 'POST':
        # Assuming you are using a form to save the data
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            # Capture internal or external based on the category
            transaction_category = form.cleaned_data.get('transaction_category')

            # If internal, save the internal_option
            if transaction_category == 'internal':
                internal_option = form.cleaned_data.get('internal_option')
                expense = form.save(commit=False)
                expense.internal_option = internal_option
                expense.save()

            # If external, save the external_type
            elif transaction_category == 'external':
                external_type = form.cleaned_data.get('external_type')
                expense = form.save(commit=False)
                expense.external_type = external_type
                expense.save()

            # If no specific category, just save the form
            else:
                expense = form.save()

            return redirect('success_url')  # Redirect to success page

    else:
        form = ExpenseForm()

    return render(request, 'xp/expense_form.html', {'form': form})


from django.shortcuts import render
from django.db.models import Q
from .models import Expense  # Assuming you're searching through the 'Expense' model

def search_view(request):
    search_query = request.GET.get('search', '')
    expenses = Expense.objects.all()

    if search_query:
        # Perform a case-insensitive search across multiple fields
        expenses = expenses.filter(
            Q(item_name__icontains=search_query) |
            Q(item_type__icontains=search_query) |
            Q(payment_category__icontains=search_query) |
            Q(transaction_category__icontains=search_query) |
            Q(transaction_details__icontains=search_query)
        )

    return render(request, 'xp/item_form.html', {'expenses': expenses, 'search_query': search_query})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Expense

def update_item(request):
    if request.method == 'POST':
        # Get the expense ID from the POST data
        expense_id = request.POST.get('id')
        if not expense_id:
            return JsonResponse({'error': 'ID is required'}, status=400)

        # Get the Expense object or return a 404 if it doesn't exist
        expense = get_object_or_404(Expense, id=expense_id)

        # Update regular fields
        expense.item_type = request.POST.get('item_type')
        expense.item_name = request.POST.get('item_name')
        expense.payment_category = request.POST.get('transaction_option')
        expense.transaction_category = request.POST.get('transaction_category')
        expense.amount = request.POST.get('amount')
        expense.transaction_date = request.POST.get('transaction_date')

        # Handle file uploads
        if 'bill_photo' in request.FILES:
            expense.bill_photo = request.FILES['bill_photo']
        if 'gst_photo' in request.FILES:
            expense.gst_photo = request.FILES['gst_photo']
        if 'voucher_number' in request.POST:
            expense.voucher_number = request.POST.get('voucher_number')

        # If there are transaction-related fields, set them accordingly
        if expense.transaction_category == 'internal':
            expense.internal_option = request.POST.get('internal_option', '')
        elif expense.transaction_category == 'external':
            expense.external_detail = request.POST.get('external_type', '')

        # Save the updated object
        expense.save()

        return JsonResponse({'message': 'Item updated successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)


    

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense
from datetime import datetime

def generate_evoucher_number():
    # Get the current date
    current_date = datetime.now()
    
    # Format the year as 'yy' and month as 'mm'
    year_month = current_date.strftime('%y%m')  # e.g., '2412' for December 2024
    
    # Query the database for the last voucher matching the current year_month prefix
    last_voucher = Expense.objects.filter(evoucher_number__startswith=f"XPEV{year_month}").order_by('-evoucher_number').first()

    if last_voucher:
        # Extract the number part from the last voucher and increment it
        last_number = int(last_voucher.evoucher_number[-4:])
        next_number = last_number + 1
    else:
        # If no voucher exists for this month, start from 1
        next_number = 1

    # Format the counter with leading zeros
    counter_str = str(next_number).zfill(4)

    # Combine everything into the final voucher number
    evoucher_number = f"XPEV{year_month}{counter_str}"
    
    return evoucher_number


def export_vouchers(request):
    """
    View for exporting vouchers to Excel, PDF, or CSV.
    """
    # Add logic for exporting data based on request parameters (e.g., export format)
    export_format = request.GET.get('format', 'xlsx')  # Can be 'xlsx', 'pdf', or 'csv'
    
    if export_format == 'xlsx':
        return export_to_xlsx(request)
    elif export_format == 'pdf':
        return export_to_pdf(request)
    elif export_format == 'csv':
        return export_to_csv(request)
    else:
        return JsonResponse({'error': 'Invalid export format'})

def export_to_xlsx(request):
    """
    Helper function to export vouchers to XLSX format with absolute file download links.
    """
    import xlsxwriter
    from io import BytesIO
    from django.conf import settings

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=vouchers.xlsx'

    # Create an in-memory workbook
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Vouchers')

    # Define column headers
    headers = ['Voucher Number', 'Item Type', 'Item Name', 'Transaction Category', 
               'T Details', 'Amount', 'Transaction Date', 'Uploaded File', 'Payment Mode']
    worksheet.write_row(0, 0, headers)

    # Fetch data
    expenses = Expense.objects.all()

    # Construct site URL for absolute media file links
    site_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash

    # Write data rows
    row = 1
    for expense in expenses:
        # Combine internal and external options, assuming one is None
        transaction_details = expense.internal_option or expense.external_type or ''

        # Construct absolute file URL if available
        uploaded_file_url = ""
        if expense.proof_photo:  # Ensure there's a file uploaded
            uploaded_file_url = f"{site_url}/download/{expense.proof_photo.name}"

        # Write data to the row
        worksheet.write_row(row, 0, [
            str(expense.evoucher_number or "N/A"),  # Handle None by showing "N/A"
            expense.item_type or "N/A",
            expense.item_name or "N/A",
            expense.transaction_category or "N/A",
            transaction_details,
            expense.amount or 0,  # Default to 0 for missing amounts
            expense.transaction_date.strftime('%Y-%m-%d') if expense.transaction_date else "N/A",
            uploaded_file_url,  # Absolute URL for download
            expense.payment_mode or "N/A",
        ])

        # Add hyperlink to the file URL if available
        if uploaded_file_url:
            worksheet.write_url(row, 7, uploaded_file_url, string="Download File")

        row += 1

    # Close the workbook
    workbook.close()

    # Write the workbook content to the response
    response.write(output.getvalue())
    output.close()
    return response

from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO

def export_to_pdf(request):
    """
    Helper function to export vouchers to PDF format with absolute file download links.
    """
    vouchers = Expense.objects.all()  # Fetch the vouchers you want to export

    # Create the PDF content dynamically (HTML content as a string)
    html_content = """
    <html>
    <head>
        <style>
            table {border-collapse: collapse; width: 100%;}
            th, td {border: 1px solid #ddd; padding: 8px; text-align: left;}
            a {color: blue; text-decoration: none;}
        </style>
    </head>
    <body>
        <h2>E-Voucher Export</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 20%; border: 1px solid #ddd; padding: 8px;">Applied Date</th>
                    <th style="width: 18%; border: 1px solid #ddd; padding: 8px;">User</th>
                    <th style="width: 23%; border: 1px solid #ddd; padding: 8px;">EV num</th>
                    <th style="width: 20%; border: 1px solid #ddd; padding: 8px;">Item Type</th>
                    <th style="width: 15%; border: 1px solid #ddd; padding: 8px;">Remarks</th>
                    <th style="width: 18%; border: 1px solid #ddd; padding: 8px;">Payment Category</th>
                    <th style="width: 15%; border: 1px solid #ddd; padding: 8px;">T Category</th>
                    <th style="width: 15%; border: 1px solid #ddd; padding: 8px;">T Details</th>
                    <th style="width: 15%; border: 1px solid #ddd; padding: 8px;">Amount</th>
                    <th style="width: 20%; border: 1px solid #ddd; padding: 8px;">Transaction Date</th>

                    <th style="width: 15%; border: 1px solid #ddd; padding: 8px;">Payment Mode</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Loop through the vouchers and add them to the table
    for voucher in vouchers:
        # Construct absolute file URL if available
        uploaded_file_url = request.build_absolute_uri(voucher.proof_photo.url) if voucher.proof_photo else ''

        html_content += f"""
        <tr>
            <td>{voucher.date}</td>
            <td>{voucher.created_by}</td>
            <td>{voucher.evoucher_number}</td>
            <td>{voucher.item_type}</td>
            <td>{voucher.item_name}</td>
            <td>{voucher.transaction_option}</td>
            <td>{voucher.transaction_category}</td>
            <td>{voucher.transaction_details}</td>
            <td>{voucher.amount}</td>
            <td>{voucher.transaction_date}</td>
            
            <td>{voucher.payment_mode}</td>
        </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Convert the HTML content to PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="vouchers.pdf"'
    
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    pdf_buffer.seek(0)
    response.write(pdf_buffer.read())
    
    return response

def export_to_csv(request):
    """
    Helper function to export vouchers to CSV format with absolute file download links.
    """
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=vouchers.csv'

    writer = csv.writer(response)
    writer.writerow(['Voucher Number', 'Item Type', 'Item Name', 'Amount', 
                     'Transaction Date', 'Uploaded File', 'Payment Mode'])

    expenses = Expense.objects.all()
    for expense in expenses:
        # Construct absolute file URL if available
        uploaded_file_url = request.build_absolute_uri(f"/download/{expense.proof_photo.name}") if expense.proof_photo else ''
        writer.writerow([
            expense.evoucher_number or '',  # Handle None for evoucher_number
            expense.item_type or '',        # Handle None for item_type
            expense.item_name or '',        # Handle None for item_name
            expense.amount or '',           # Handle None for amount
            expense.transaction_date.strftime('%Y-%m-%d') if expense.transaction_date else '',  # Handle None for transaction_date
            uploaded_file_url,              # Absolute URL for the uploaded file
            expense.payment_mode or '',     # Handle None for payment_mode
        ])
    
    return response
from django.http import FileResponse, Http404
import os
from django.conf import settings

def download_proof(request, file_name):
    """
    Serve the uploaded proof file as an attachment for download.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    
    if not os.path.exists(file_path):
        raise Http404("File not found.")

    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    return response

from django.shortcuts import render
from .models import  CashVoucher

def search_vouchers(request):
    query = request.GET.get('q', '')
    vouchers = []
    cash_vouchers = []

    if query:
        # Search in Voucher and CashVoucher models
        vouchers = CashVoucher.objects.filter(
            voucher_number__icontains=query
        ) | CashVoucher.objects.filter(
            item_name__icontains=query
        )

        cash_vouchers = CashVoucher.objects.filter(
            voucher_number__icontains=query
        ) | CashVoucher.objects.filter(
            paid_to__icontains=query
        )

    context = {
        'vouchers': vouchers,
        'cash_vouchers': cash_vouchers,
        'query': query,
    }
    return render(request, 'xp/voucher_list.html', context)


import csv
from io import BytesIO
from django.http import HttpResponse
import xlsxwriter
from reportlab.pdfgen import canvas
from .models import CashVoucher  # Replace with your actual model


def export_cash_vouchers(request):
    format = request.GET.get('format', 'csv')
    vouchers = CashVoucher.objects.all()  # Adjust queryset as needed for filtering
    
    if format == 'csv':
        return export_cash_vouchers_csv(vouchers)
    elif format == 'xlsx':
        return export_cash_vouchers_xlsx(vouchers)
    elif format == 'pdf':
        return export_cash_vouchers_pdf(vouchers)
    else:
        return HttpResponse("Invalid format", status=400)


def export_cash_vouchers_csv(vouchers):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cash_vouchers.csv"'
    writer = csv.writer(response)
    
    # Write the header
    writer.writerow(['Voucher Number', 'Date', 'Paid To', 'Item Name', 'Amount', 'Transaction Date', 'Status'])
    
    # Write the data rows
    for voucher in vouchers:
        writer.writerow([
            voucher.voucher_number,
            voucher.date,
            voucher.paid_to,
            voucher.item_name,
            voucher.amount,
            voucher.transaction_date,
            voucher.status,
        ])
    
    return response


from django.http import HttpResponse
import openpyxl  # or any library you're using to generate the XLSX file

def export_cash_vouchers_xlsx(vouchers):
    # Generate your XLSX file
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Voucher Number', 'Item Name', 'Amount'])  # Example headers
    
    # Add rows for each voucher
    for voucher in vouchers:
        ws.append([voucher.voucher_number,
            voucher.date,
            voucher.paid_to,
            voucher.item_name,
            voucher.amount,
            voucher.transaction_date,
            voucher.status,])

    # Create an HTTP response with the XLSX content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Cash_Vouchers.xlsx'
    wb.save(response)
    
    return response


from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string

def export_cash_vouchers_pdf(request):
    """
    Export vouchers to PDF using a styled HTML template.
    """
    # Fetch the vouchers you want to export
    vouchers = CashVoucher.objects.all()

    # Prepare the context for the HTML template
    context = {
        'vouchers': vouchers
    }

    # Render the HTML content using Django templates
    html_content = render_to_string('xp/export_cash_vouchers_template.html', context)

    # Create an HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="CashVoucher.pdf"'

    # Convert the HTML content to PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    # Write the PDF content to the response
    pdf_buffer.seek(0)
    response.write(pdf_buffer.read())
    return response
    
from django.shortcuts import render
from django.db.models import Sum
from django.db.models import F, Func
from .models import CashVoucher
from .models import Expense  # Assuming Expense model is in the `expenses` app

from django.db.models.functions import TruncMonth


from datetime import date, datetime, timedelta


from django.shortcuts import render
from django.db.models import Sum
from django.db.models import F, Func
from .models import CashVoucher
from .models import Expense  # Assuming Expense model is in the `expenses` app
from django.db import connection
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth


from datetime import date, datetime, timedelta


from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from datetime import date, datetime

def vouchers_dashboard(request):
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
        expenses = Expense.objects.filter(date__range=(from_date, to_date)).filter(is_draft=False)
    else:
        vouchers = CashVoucher.objects.filter(created_by=user, date__range=(from_date, to_date))
        expenses = Expense.objects.filter(created_by=user, date__range=(from_date, to_date)).filter(is_draft=False)

    # Calculate total counts for each status
    total_vouchers = vouchers.count()
    approved_vouchers = vouchers.filter(status='approved').count()
    rejected_vouchers = vouchers.filter(status='rejected').count()
    pending_vouchers_count = vouchers.filter(status='pending').count()
    cleared_vouchers_count = vouchers.filter(status='paid').count()

    # Calculate total claiming amount and approved amount
    total_claiming_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_claiming_amount_cv = vouchers.aggregate(Sum('amount'))['amount__sum'] or 0
    total_approved_amount = vouchers.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0

    # Aggregate the total paid amount for expenses and vouchers
    if user.is_staff:
        paid_expenses = Expense.objects.filter(status='paid')
        paid_vouchers = CashVoucher.objects.filter(status='paid')
    else:
        paid_expenses = Expense.objects.filter(created_by=user, status='paid')
        paid_vouchers = CashVoucher.objects.filter(created_by=user, status='paid')

    # Aggregate the total paid amount
    total_paid_amount = paid_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_paid_amount_cv = paid_vouchers.aggregate(Sum('amount'))['amount__sum'] or 0

    # Total e-voucher count
    total_evouchers = expenses.count()

    # Difference between claiming and approved amounts
    claiming_approved_diff = total_claiming_amount - total_paid_amount

    # Calculate month-wise total claimed and approved amounts
    vouchers_by_month = vouchers.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_claimed=Sum('amount'),
        total_paid=Sum('amount', filter=Q(status='paid')),
        total_evoucher_amount=Sum('amount', filter=Q(status='approved'))
    ).order_by('month')
    

    months_list = []
    claimed_amounts = []
    paid_amounts = []
    evoucher_amounts = []

    for voucher in vouchers_by_month:
        months_list.append(voucher['month'].strftime('%b %Y'))
        claimed_amounts.append(voucher['total_claimed'])
        paid_amounts.append(voucher['total_paid'])
        evoucher_amounts.append(voucher['total_evoucher_amount'])

    # Item type counts for chart rendering
    item_type_counts_and_amounts = (
    expenses.values('item_type')
    .annotate(
        count=Count('item_type'),
        total_amount=Sum('amount')  # Assuming 'amount' is the field where the amount is stored
    )
)

# Transform item type counts and amounts into a dictionary
    item_type_data = {
            entry['item_type']: {
                'count': entry['count'],
                'total_amount': entry['total_amount'] if entry['total_amount'] is not None else 0
            }
            for entry in item_type_counts_and_amounts
        }

# Ensure all item types are represented, even with a count of 0
    all_item_types = [
            'fright_transportation', 'fuel_oil', 'food_grocery', 'others', 'vendor',
            'reimbursement', 'site_services', 'advances', 'travelling', 'electricity_bill',
            'internet_bill', 'postage_telegram', 'machine_repair', 'conveyance',
            'stationary_printing', 'hospitality'
        ]

    item_type_data = {item_type: item_type_data.get(item_type, {'count': 0, 'total_amount': 0}) for item_type in all_item_types}

    # Context for template rendering
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'total_vouchers': total_vouchers,
        'approved_vouchers': approved_vouchers,
        'rejected_vouchers': rejected_vouchers,
        'pending_vouchers_count': pending_vouchers_count,
        'total_claiming_amount': total_claiming_amount,
        'total_approved_amount': total_approved_amount,
        'total_evouchers': total_evouchers,
        'claiming_approved_diff': claiming_approved_diff,
        'months_list': months_list,
        'claimed_amounts': claimed_amounts,
        'paid_amounts': paid_amounts,
        'total_paid_amount': total_paid_amount,
        'cleared_vouchers_count': cleared_vouchers_count,
        'total_claiming_amount_cv': total_claiming_amount_cv,
        'total_paid_amount_cv': total_paid_amount_cv,
        'evoucher_amounts': evoucher_amounts,
        'item_type_data': item_type_data,  # Pass item type data for chart
    }

    return render(request, 'xp/dashboard.html', context)


from django.http import JsonResponse
from django.shortcuts import render
from .models import CashVoucher, User
from app.models import Zone, UserProfile
from datetime import timedelta, date

def get_users_by_zone(request):
    zone_id = request.GET.get('zone_id')
    users = []
    if zone_id:
        selected_zone = Zone.objects.get(id=zone_id)
        users_in_zone = UserProfile.objects.filter(zone=selected_zone).values('user__id', 'user__username')
        users = [{'id': user['user__id'], 'username': user['user__username']} for user in users_in_zone]

    return JsonResponse({'users': users})

# from datetime import date, timedelta
# from django.shortcuts import render
# from .models import User, Zone, CashVoucher, UserProfile

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
        expenses = queryset.filter(
    Q(proof_photo__gt='') | Q(transaction_option='voucher')).exclude(status='paid').filter(is_draft=False).filter(Q(cashvoucher__isnull=True) | Q(cashvoucher__status='approved'))
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


from django.shortcuts import render
from .models import User, CashVoucher, Expense
from datetime import datetime

def pay_now(request, user_id):
    selected_user = User.objects.get(id=user_id)
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
    payment_details = None
    if request.method == 'POST':
        # Get form data
        print("POST Data:", request.POST)
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
    

    return render(request, 'xp/pay_now.html', {
        'selected_user': selected_user,
        'expenses': expenses,
        'total_amount_to_be_paid': total_amount_to_be_paid,
        'transaction_id': transaction_id,
        'from_date': from_date,
        'to_date': to_date,
        'selected_filter': selected_filter,
        'payment_details': payment_details,  
    })
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import Expense, Payment, User, Notification
from decimal import Decimal
from datetime import datetime

def process_payment(request):
    if request.method == "POST":
        try:
            # Debugging: Print Request Data
            print("Request POST Data:", request.POST)
            print("Files Data:", request.FILES)

            # Get and validate form data
            user_id = request.POST.get('user_id')
            transaction_id = request.POST.get('transaction_id')
            amount = request.POST.get('amount')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            screenshot = request.FILES.get('screenshot')

            # Debugging: Check if all required data is available
            print(f"User ID: {user_id}")
            print(f"Transaction ID: {transaction_id}")
            print(f"Amount: {amount}")
            print(f"From Date: {from_date}")
            print(f"To Date: {to_date}")
            print(f"Screenshot: {screenshot}")

            # Check if any data is missing
            if not all([user_id, transaction_id, amount, from_date, to_date, screenshot]):
                messages.error(request, "All fields are required.")
                return redirect('pay_now', user_id=user_id)

            # Parse and validate data
            selected_user = get_object_or_404(User, id=user_id)
            amount_paid = Decimal(amount)
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()

            # Debugging: Print parsed data
            print(f"Parsed From Date: {from_date_obj}")
            print(f"Parsed To Date: {to_date_obj}")
            print(f"Amount Paid: {amount_paid}")

            # Get expenses within the specified range
            expenses_query = Expense.objects.filter(
                created_by=selected_user, 
                status="pending",
                date__range=[from_date_obj, to_date_obj]
            )

            # Debugging: Check if expenses are fetched correctly
            print("Filtered Expenses Query:", expenses_query)

            total_amount_to_be_paid = expenses_query.aggregate(total=Sum('amount'))['total'] or Decimal(0)
            print(f"Total Amount to be Paid: {total_amount_to_be_paid}, Amount Paid: {amount_paid}")

            # Check if total amount to be paid is greater than the paid amount
            if amount_paid > total_amount_to_be_paid:
                messages.error(request, "Amount exceeds total amount to be paid.")
                return redirect('pay_now', user_id=user_id)

            # Process payment
            remaining_amount = amount_paid
            paid_amount = Decimal(0)

            for expense in expenses_query:
                # Debugging: Show each expense being processed
                print(f"Processing Expense ID: {expense.id}, Amount: {expense.amount}, Remaining Amount: {remaining_amount}")

                if remaining_amount <= 0:
                    print("No remaining amount to pay.")
                    break

                if expense.amount <= remaining_amount:
                    paid_amount += expense.amount
                    remaining_amount -= expense.amount
                    expense.status = "paid"
                else:
                    paid_amount += remaining_amount
                    expense.amount -= remaining_amount
                    remaining_amount = Decimal(0)

                # Debugging: Show updated expense details
                print(f"Updated Expense ID: {expense.id}, Status: {expense.status}, Remaining Amount: {expense.amount}")
                expense.save()

                # Send notification when the voucher status is changed to 'paid'
                notification = Notification.objects.create(
                    user=expense.created_by,
                    title="Voucher Paid",
                    message=f"Voucher number {expense.evoucher_number} of ₹ {expense.amount} has been paid.",
                )
                notification.save()

            # Debugging: Check if any amount was paid
            print(f"Total Paid Amount: {paid_amount}")

            if paid_amount == 0:
                messages.warning(request, "No vouchers were paid.")
                return redirect('pay_now', user_id=user_id)

            # Save payment record
            payment = Payment.objects.create(
                paid_to=selected_user,
                transaction_id=transaction_id,
                amount=paid_amount,
                from_date=from_date_obj,
                to_date=to_date_obj,
                screenshot=screenshot,
            )

            # Debugging: Payment record created
            print(f"Payment Record Created: {payment}")
            messages.success(request, f"Payment of {paid_amount} processed successfully!")
            return redirect('dashboard')

        except Exception as e:
            # Debugging: Catch any exception and log it
            print(f"Error occurred: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('pay_now', user_id=request.POST.get('user_id'))

    messages.error(request, "Invalid request method.")
    return redirect('pay_now', user_id=request.POST.get('user_id')) # Fallback if method is not POST  # Fallback if method is not POST  # Fallback if method is not POST


from django.shortcuts import render, redirect
from django.contrib import messages

def payment_success(request):
    # Add a success message
    messages.success(request, "Your payment has been successfully processed.")
    return redirect('payable')  # Redirect to the `payable` page or any relevant page



@login_required
def payments(request):
    query = request.GET.get('q', '')  # Search query
    user_id = request.GET.get('user_id')  # Get the user ID from the request
    
    user = request.user

    # Start with the base queryset depending on the user role
    if user.is_superuser:  # Admin - View all users' payments
        user_payments = Payment.objects.all().order_by('created_at')
    else:  # Regular user - View only own payments
        user_payments = Payment.objects.filter(paid_to=user).order_by('created_at')

    # If a user ID is selected, filter payments based on that user
    if user_id:
        user_payments = user_payments.filter(paid_to__id=user_id)

    # Apply search filters if a query is provided
    if query:
        user_payments = user_payments.filter(
            Q(transaction_id__icontains=query) |
            Q(paid_to__username__icontains=query) |
            Q(amount__icontains=query) |
            Q(from_date__icontains=query) |
            Q(to_date__icontains=query)
        )

    # Prepare the list of payments with relevant details
    users = User.objects.all()  # Order users by username
    
    payments_with_details = []
    for payment in user_payments:
        payments_with_details.append({
            'transaction_id': payment.transaction_id,
            'paid_to': payment.paid_to,
            'amount': payment.amount,
            'from_date': payment.from_date,
            'to_date': payment.to_date,
            'screenshot': payment.screenshot.url if payment.screenshot else None,
            'created_at': payment.created_at,
        })

    # Pass the filtered or unfiltered queryset with payment details and users to the template
    return render(request, 'xp/user_payment_history.html', {
        'payments': payments_with_details,
        'users': users,  # Add users here to be used in the template
        'selected_user_id': user_id,  # Pass the selected user ID back to the template
    })

import csv
from io import StringIO
from django.http import HttpResponse
from openpyxl import Workbook
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from reportlab.pdfgen import canvas

from .models import Payment  # Import your Payment model

def export_payments(request):
    # Get the requested format from the query parameters
    file_format = request.GET.get('format', 'csv')
    payments = Payment.objects.all()  # Replace with filtered queryset if needed

    if file_format == 'csv':
        return export_as_csv(payments,request)
    elif file_format == 'xlsx':
        return export_as_xlsx(payments,request)
    elif file_format == 'pdf':
        return export_as_pdf(payments)
    else:
        return HttpResponse("Invalid format requested", status=400)

# CSV Export
import csv
from django.http import HttpResponse
from django.utils.timezone import now
from django.conf import settings

def export_as_csv(payments, request):
    """
    Exports payment records as a CSV file with absolute file download links (if applicable).
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payments_{now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Transaction ID', 'Paid To', 'Amount', 'From', 'To', 'Date', 'Uploaded Proof'])

    # Construct site URL for absolute file links
    site_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash

    for payment in payments:
        # Generate downloadable proof link
        if hasattr(payment, 'proof_photo') and payment.proof_photo:
            proof_file_url = f"{site_url}/download/{payment.proof_photo.name}"
        else:
            proof_file_url = 'No File'

        writer.writerow([
            payment.transaction_id or 'N/A',
            payment.paid_to or 'N/A',
            payment.amount or 0.00,
            payment.from_date.strftime('%Y-%m-%d') if payment.from_date else 'N/A',
            payment.to_date.strftime('%Y-%m-%d') if payment.to_date else 'N/A',
            payment.created_at.strftime('%d %b %Y, %H:%M') if payment.created_at else 'N/A',
            proof_file_url  # Downloadable link
        ])

    return response

# XLSX Export
from openpyxl import Workbook
from io import BytesIO
from django.http import HttpResponse
from django.utils.timezone import now

def export_as_xlsx(queryset, request):
    """
    Exports payment records as an Excel (.xlsx) file with absolute downloadable screenshot URLs.
    """
    # Create a new workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Payments"

    # Define headers
    headers = ["Transaction ID", "Paid To", "Amount", "From Date", "To Date", "Screenshot URL", "Date"]
    ws.append(headers)

    # Construct site URL for absolute file links
    site_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash

    # Populate data rows
    for payment in queryset:
        # Generate downloadable screenshot link
        screenshot_url = f"{site_url}/download/{payment.screenshot.name}" if hasattr(payment, 'screenshot') and payment.screenshot else "No Screenshot"

        ws.append([
            payment.transaction_id or "N/A",
            str(payment.paid_to) if payment.paid_to else "N/A",
            payment.amount or 0.00,
            payment.from_date.strftime("%Y-%m-%d") if payment.from_date else "N/A",
            payment.to_date.strftime("%Y-%m-%d") if payment.to_date else "N/A",
            screenshot_url,
            payment.created_at.strftime("%Y-%m-%d %H:%M:%S") if payment.created_at else "N/A",
        ])

    # Save workbook to a BytesIO buffer
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Return as an HTTP response
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="payments_{now().strftime("%Y%m%d")}.xlsx"'

    return response

# PDF Export
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Payment  # Assuming Payment is the model name, replace with actual model

def export_as_pdf(request):
    """
    Export payment history to PDF using a styled HTML template.
    """
    # Fetch the payments you want to export; you can filter based on request parameters
    payments = Payment.objects.all()

    # Prepare context for the template
    context = {
        'payments': payments
    }

    # Render the HTML content using the template
    html_content = render_to_string('xp/export_payments_template.html', context)

    # Create an HttpResponse object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payments.pdf"'

    # Generate the PDF from HTML
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    # Handle PDF generation errors
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    # Write the generated PDF to the response
    pdf_buffer.seek(0)
    response.write(pdf_buffer.read())
    return response
from django.http import JsonResponse

def get_monthwise_data(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Default to current month if no filters provided
    if not from_date or not to_date:
        today = date.today()
        first_day = today.replace(day=1)
        last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        from_date = first_day
        to_date = last_day

    # Convert to date objects
    from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
    to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

    # Filter vouchers and expenses based on the date range
    vouchers = CashVoucher.objects.filter(date__range=(from_date, to_date))
    expenses = Expense.objects.filter(date__range=(from_date, to_date))

    # Get month-wise data
    vouchers_by_month = vouchers.annotate(month=TruncMonth('date')).values('month').annotate(
        total_claimed=Sum('amount'),
        total_paid=Sum('amount', filter=Q(status='paid'))
    ).order_by('month')

    expenses_by_month = expenses.annotate(month=TruncMonth('date')).values('month').annotate(
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

    for expense in expenses_by_month:
        if expense['month'].strftime('%b %Y') not in months_list:
            months_list.append(expense['month'].strftime('%b %Y'))
            claimed_amounts.append(expense['total_claimed'])
            paid_amounts.append(expense['total_paid'])

    return JsonResponse({
        'months_list': months_list,
        'claimed_amounts': claimed_amounts,
        'paid_amounts': paid_amounts,
    })


from django.shortcuts import render

def drafts_list(request):
    # Fetch draft items from the database (Example: filter by a 'draft' status)
    drafts = Expense.objects.filter(status='draft')
    return render(request, 'app/drafts_list.html', {'drafts': drafts})


# views.py
from django.http import JsonResponse
from .models import Conveyance

def get_price_per_km(request):
    vehicle_type = request.GET.get('vehicle_type')

    if not vehicle_type:
        return JsonResponse({'error': 'Vehicle type is required'}, status=400)

    try:
        # Fetch the conveyance object based on the vehicle type
        conveyance = Conveyance.objects.get(vehicle_type=vehicle_type)
        return JsonResponse({'price_per_km': float(conveyance.price_per_km)})
    except Conveyance.DoesNotExist:
        return JsonResponse({'error': 'Price per kilometer not found for this vehicle type'}, status=404)



from django.shortcuts import render

def test(request):
    return render(request, 'xp/test.html')



def erp_software(request):
    return render(request, 'xp/erp-software.html')  # Ensure the path is correct
