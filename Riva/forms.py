import datetime
from django import forms
from .models import Enquiry, Products, Executive,quotation





class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = [
            'companyname',
            'customername',
            'email',
            'contact',
            'location',
            'status',
            'products',
            'closuredate',
            'executive',
            'files',
            'remarks',
            'refrence',   
            'subproduct',     
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 NOTHING IS REQUIRED
        for field in self.fields.values():
            field.required = False
            field.widget.attrs['class'] = 'form-control'

    # ✅ OPTIONAL contact validation
    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        if contact and not str(contact).isdigit():
            raise forms.ValidationError("Contact number must be numeric.")
        return contact

    # ✅ OPTIONAL email validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")
        return email

    # ✅ OPTIONAL location (NO required check)
    def clean_location(self):
        return self.cleaned_data.get('location')

    # ✅ OPTIONAL closure date
    def clean_closuredate(self):
        return self.cleaned_data.get('closuredate')


class QuotationForm(forms.ModelForm):
    class Meta:
        model = quotation
        fields = ['quote', 'baseamount', 'boq', 'finalamount']

    def __init__(self, *args, **kwargs):
        # Pass `enquiry_instance` as an additional parameter
        enquiry_instance = kwargs.pop('enquiry_instance', None)
        super().__init__(*args, **kwargs)

        if enquiry_instance:
            # Store the enquiry instance details for display
            self.enquiry_display = {
                "id": enquiry_instance.id,
                "company_name": enquiry_instance.companyname,
                "company_gst": enquiry_instance.companygst,
                "company_pan": enquiry_instance.companypan,
            }

from .models import ConfirmedOrder
class ConfirmedOrderForm(forms.ModelForm):
    class Meta:
        model = ConfirmedOrder
        fields = ['project_closing_date', 'workorder', 'boq']
        widgets = {
            'project_closing_date': forms.DateInput(
                attrs={
                    'class': 'form-control', 
                    'type': 'date', 
                    'id': 'fodate', 
                    'placeholder': 'Select a date', 
                    'required': 'true'
                }
            ),
            'workorder': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'workorder'}),
            'boq': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'boq'}),
        }