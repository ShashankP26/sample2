from django.http import HttpResponse
from weasyprint import HTML  # WeasyPrint to generate PDF
from django.shortcuts import render, redirect ,get_object_or_404
from .models import GeneralReport


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import GeneralReport

def base(request):
    return render(request ,'base.html')

def home(request):
    return render(request ,'home.html')

def servicereport(request):
    return render(request, 'servicereport.html')
def  success(request):
    return render(request,'success')
# -----------------------------MaintenanceChecklist-----------------------------------

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MaintenanceChecklist, Machine ,MaintenanceChecklistAttachment
from datetime import date

@login_required
def maintenance_checklist(request):
    machines = Machine.objects.all()

    if request.method == 'POST':
        machine_id = request.POST.get('machine_name')
        visit_date = request.POST.get('visit_date')
        supply_voltage = request.POST.get('supply_voltage')
        supply_voltage_details = request.POST.get('supply_voltage_details', '')
        current_load = request.POST.get('current_load')
        current_load_details = request.POST.get('current_load_details', '')
        observations = request.POST.getlist('observation[]')
        attachments = request.FILES.getlist('attachment[]')  # Get multiple attachments

        # Capture the current date when the form is submitted
        current_date = date.today()

        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return HttpResponse("Machine not found.", status=404)

        # Concatenate observations into a single string
        notes = "\n".join(observations)

        # Create the Maintenance Checklist entry
        checklist = MaintenanceChecklist(
            inspector_name=request.user.username,  # Auto-fill with logged-in user's username
            machine=machine,
            visit_date=visit_date,
            notes=f"Supply Voltage: {supply_voltage} ({supply_voltage_details})\n"
                  f"Current Load: {current_load} ({current_load_details})\n"
                  f"Observations:\n{notes}",
            date=current_date  # Store the current date
        )
        checklist.save()

        # Save each uploaded attachment
        for attachment in attachments:
            MaintenanceChecklistAttachment.objects.create(checklist=checklist, file=attachment)

        # Redirect after successful save (customize as needed)
        return redirect('maintenance_checklist')  # Adjust this to your URL name

    return render(request, 'maintenance_checklist.html', {'machines': machines})



from django.shortcuts import render
from .models import MaintenanceChecklist
# maintenance_checklist_records

def maintenance_checklist_records(request):
    checklists = MaintenanceChecklist.objects.all().order_by('-date')  # Order by most recent
    query = request.GET.get('search', '')
    if query:
        checklists = checklists.filter(
            Q(inspector_name__icontains=query) |
            Q(date__icontains=query) |
            Q(machine__name__icontains=query) |
            Q(visit_date__icontains=query) |
            Q(notes__icontains=query)
        )

    context = {
        'checklists': checklists,
        'search_query': query,
    }
    return render(request, 'maintenance_checklist_viewing.html', context)
# -----------------------------MOM-----------------------------------



from django.shortcuts import render, redirect
from .models import MOM, Attachment
from django.utils.timezone import now

def mom(request):
    if request.method == 'POST':
        # Create the meeting instance from POST data
        meeting = MOM(
            topic=request.POST['topic'],
            organize=request.POST['organize'],
            client=request.POST['client'],
            meeting_chair=request.POST['meeting_chair'],
            location=request.POST['location'],
            date=request.POST['date'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            duration=request.POST['duration'],
            updated_by=request.user.username,  # Set logged-in user as the updater
            meeting_conclusion=request.POST['meeting_conclusion'],
            summary_of_discussion=request.POST['summary_of_discussion'],
            attendees=request.POST.getlist('attendees[]'),
            apologies=request.POST.getlist('apologies[]'),
            agenda=request.POST.getlist('agenda[]')
        )

        # Save the meeting instance to the database
        meeting.save()

        # Save the uploaded files (attachments)
        for attachment_file in request.FILES.getlist('attachment[]'):
            attachment = Attachment(file=attachment_file, meeting=meeting)
            attachment.save()
    return render(request, 'mom.html')


def mom_records(request):
    # Fetch all MOM records ordered by the most recent
    mom_records = MOM.objects.all().order_by('-created_at')  # Adjust the order as needed
    search_query = request.GET.get('search', '')
    if search_query:
        mom_records = mom_records.filter(
            Q(topic__icontains=search_query) |
            Q(organize__icontains=search_query) |
            Q(client__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(meeting_chair__icontains=search_query) |
            Q(date__icontains=search_query)
        )

    context = {
        'mom_records': mom_records,
        'search_query': search_query,
    }
    return render(request, 'mom_viewing.html', context)

def mom_detail(request, mom_id):
    mom = get_object_or_404(MOM, id=mom_id)
    return render(request, 'mom_detail.html', {'mom': mom})


# --------------------------generalreport-----------------------------

from django.shortcuts import render, redirect
from .models import GeneralReport, Site

def generalreportsviewing(request):
    query = request.GET.get('search', '')
    reports = GeneralReport.objects.all()

    if query:
        reports = reports.filter(
            Q(site__name__icontains=query) |
            Q(date_of_visit__icontains=query) |
            Q(point1__icontains=query) |
            Q(point2__icontains=query) |
            Q(point3__icontains=query) |
            Q(point4__icontains=query) |
            Q(notes__icontains=query)
        )

    context = {
        'reports': reports,
        'search_query': query,
    }
    return render(request, 'generalreportviewing.html', context)






from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_pdf(request, report_id):
    # Fetch the report object
    report = GeneralReport.objects.get(id=report_id)
    
    # Create an HTTP response with content type 'application/pdf'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report_id}.pdf"'

    # Create a canvas (PDF)
    pdf_canvas = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Get the dimensions of the page

    # Set the font
    pdf_canvas.setFont("Helvetica-Bold", 16)
    
    # Title
    pdf_canvas.drawString(100, height - 40, f"General Report for Site: {report.site.name}")
    
    # Draw a line under the title
    pdf_canvas.setStrokeColor(colors.black)
    pdf_canvas.line(100, height - 45, width - 100, height - 45)

    # Set font for the body of the report
    pdf_canvas.setFont("Helvetica", 12)
    
    # Report Details
    pdf_canvas.drawString(100, height - 70, f"Date of Visit: {report.date_of_visit}")

    # Add spacing
    y_position = height - 100
    
    # Points Section
    pdf_canvas.drawString(100, y_position, "Points:")
    y_position -= 20  # Move down after the Points label

    points = [report.point1, report.point2, report.point3, report.point4]
    for i, point in enumerate(points, start=1):
        pdf_canvas.drawString(120, y_position, f"{i}. {point}")
        y_position -= 18  # Adjust spacing between each point

    # Notes Section
    y_position -= 20
    pdf_canvas.drawString(100, y_position, "Notes:")
    y_position -= 18
    pdf_canvas.drawString(120, y_position, report.notes or "No notes provided.")
    
    # Footer with page number
    pdf_canvas.setFont("Helvetica", 10)
    pdf_canvas.drawString(100, 30, f"Generated on: {report.date_of_visit}")
    pdf_canvas.drawString(width - 100 - 50, 30, f"Page 1")

    # Save the PDF document
    pdf_canvas.showPage()
    pdf_canvas.save()

    # Return the PDF as an HTTP response
    return response

from django.db.models import Q

def generalreport(request):
    sites = Site.objects.all()  # Get all available sites
    if request.method == 'POST':
        # Fetch the Site instance by ID from the POST data
        site_id = request.POST.get('site')
        try:
            site_instance = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return render(request, 'error_template.html', {'error': 'Invalid site selected'})

        # Create a new GeneralReport instance
        GeneralReport.objects.create(
            site=site_instance,
            date_of_visit=request.POST.get('date_of_visit'),
            point1=request.POST.get('point1'),
            point2=request.POST.get('point2'),
            point3=request.POST.get('point3'),
            point4=request.POST.get('point4'),
            notes=request.POST.get('notes'),
            attachment=request.FILES.get('attachment')
        )

        # Redirect to the viewing page
        return redirect('generalreportsviewing')  # Ensure this URL name is correct

    # Fetch all saved reports to display
    reports = GeneralReport.objects.all()
    return render(request, 'generalreport.html', {'reports': reports, 'sites': sites})
# ------------servicereport--------------------

from django.shortcuts import render, redirect
from .models import ServiceReport, ElectronicItem, ElectronicItemStatus, ElectronicPanel ,ElectronicPanelStatus ,WastewaterParameterStatus
from .models import ChemicalItem ,ChemicalItemStatus ,Pump ,PumpStatus ,MiscellaneousItem ,MiscellaneousItemStatus ,WastewaterParameter
from .models import MachineRunTime ,Tool ,ToolStatus ,State
def servicereport(request):
    tools = Tool.objects.all()
    state_name = request.POST.get("state")
    state_instance = State.objects.get(name=state_name) if state_name else None
    service_report = None  # Initialize service_report to None


    if request.method == 'POST':
        # Static fields from the form (using .get() with default values to avoid errors)
        service_name = request.POST.get('service_name', '')
        date_of_visit = request.POST.get('date_of_visit', '')
        zone = request.POST.get('zone', '')
        phone_no = request.POST.get('phone_no', '')
        reason_of_visit = request.POST.get('reason_of_visit', '')
        in_time = request.POST.get('in_time', '')
        out_time = request.POST.get('out_time', '')

        # Customer Information
        customer_name = request.POST.get('customer_name', '')
        contact_number = request.POST.get('contact_number', '')
        location = request.POST.get('location', '')
        state = request.POST.get('state', '')
        date_of_complaint = request.POST.get('date_of_complaint', '')
        status_of_call = request.POST.get('status_of_call', '')

        # Create the ServiceReport
        service_report = ServiceReport.objects.create(
            service_name=service_name,
            date_of_visit=date_of_visit,
            zone=zone,
            phone_no=phone_no,
            reason_of_visit=reason_of_visit,
            in_time=in_time,
            out_time=out_time,
            customer_name=customer_name,
            contact_number=contact_number,
            location=location,
            state=state_instance,
            date_of_complaint=date_of_complaint,
            status_of_call=status_of_call
        )

        electronic_panels = ElectronicPanel.objects.all()
        electronic_items = ElectronicItem.objects.all()
        chemical_items = ChemicalItem.objects.all()
        pumps = Pump.objects.all()
        miscellaneous_items = MiscellaneousItem.objects.all()
        wastewater_parameters = WastewaterParameter.objects.all()
        machine_runtimes =MachineRunTime.objects.all()
        states = State.objects.all()  # Get all states from the database

        service_report.certified_by = request.POST.get('certified_by', '')
        service_report.certified_by_name = request.POST.get('certified_by_name', '')
        service_report.approved_by = request.POST.get('approved_by', '')
        service_report.approved_by_name = request.POST.get('approved_by_name', '')
        remarks = []
        spares = []
        # Collect all remarks from form data
        for key, value in request.POST.items():
            if key.startswith('remark_') and value.strip():
                remarks.append(value.strip())
                # Collect spares details
        for key, value in request.POST.items():
            if key.startswith('spare_') and value.strip():
                spares.append(value.strip())


        # Join all remarks into a single string separated by newlines
        service_report.other_remarks = '\n'.join(remarks)
        service_report.spares_details = '\n'.join(spares)
        service_report.save()     
        # Handle dynamic electronic items and their statuses
        for item in electronic_items:
            checked = request.POST.get(f'checked_{item.id}') == 'on'
            repair = request.POST.get(f'repair_{item.id}') == 'on'
            replacement = request.POST.get(f'replacement_{item.id}') == 'on'
            remark = request.POST.get(f'remark_{item.id}')

            # Create an entry in ElectronicItemStatus for each item
            ElectronicItemStatus.objects.create(
                report=service_report,
                item=item,
                checked=checked,
                repair=repair,
                replacement=replacement,
                remark=remark
            )

        # Handle dynamic electronic panels and their statuses
        for panel in electronic_panels:
            checked = request.POST.get(f'checked_{panel.id}') == 'on'
            repair = request.POST.get(f'repair_{panel.id}') == 'on'
            replacement = request.POST.get(f'replacement_{panel.id}') == 'on'
            remark = request.POST.get(f'remark_{panel.id}')

            # Create an entry in ElectronicPanelStatus for each panel
            ElectronicPanelStatus.objects.create(
                report=service_report,
                panel=panel,
                checked=checked,
                repair=repair,
                replacement=replacement,
                remark=remark
            )

        
        for item in chemical_items:
            checked = request.POST.get(f'checked_chemical_{item.id}') == 'on'
            repair = request.POST.get(f'repair_chemical_{item.id}') == 'on'
            replacement = request.POST.get(f'replacement_chemical_{item.id}') == 'on'
            remark = request.POST.get(f'remark_chemical_{item.id}')

            # Create ChemicalItemStatus entry
            ChemicalItemStatus.objects.create(
                report=service_report,
                item=item,
                checked=checked,
                repair=repair,
                replacement=replacement,
                remark=remark
            )

        for pump in pumps:
            checked = request.POST.get(f'checked_pump_{pump.id}') == 'on'
            repair = request.POST.get(f'repair_pump_{pump.id}') == 'on'
            replacement = request.POST.get(f'replacement_pump_{pump.id}') == 'on'
            remark = request.POST.get(f'remark_pump_{pump.id}')

            # Create PumpStatus entry
            PumpStatus.objects.create(
                report=service_report,
                pump=pump,
                checked=checked,
                repair=repair,
                replacement=replacement,
                remark=remark
            )

        for item in miscellaneous_items:
            checked = request.POST.get(f'checked_miscellaneous_{item.id}') == 'on'
            repair = request.POST.get(f'repair_miscellaneous_{item.id}') == 'on'
            replacement = request.POST.get(f'replacement_miscellaneous_{item.id}') == 'on'
            remark = request.POST.get(f'remark_miscellaneous_{item.id}')

            # Create MiscellaneousItemStatus entry
            MiscellaneousItemStatus.objects.create(
                report=service_report,
                item=item,
                checked=checked,
                repair=repair,
                replacement=replacement,
                remark=remark
            )
        
        for parameter in wastewater_parameters:
            checked = request.POST.get(f'checked_wastewater_{parameter.id}') == 'on'
            repair = request.POST.get(f'repair_wastewater_{parameter.id}') == 'on'
            replacement = request.POST.get(f'replacement_wastewater_{parameter.id}') == 'on'
            remark = request.POST.get(f'remark_wastewater_{parameter.id}')

            # Create WastewaterParameterStatus entry
            WastewaterParameterStatus.objects.create(
                report=service_report,
                parameter=parameter,
                checked=checked,
                repair=repair,
                replacement=replacement,
                remark=remark
            )

        run_cycle_count = int(request.POST.get('run_cycle_count', 1))

        for cycle_number in range(1, run_cycle_count + 1):
            run_time = request.POST.get(f'run_time_{cycle_number}')
            end_time = request.POST.get(f'end_time_{cycle_number}')
            checked = 'checked' in request.POST.getlist(f'checked_{cycle_number}')
            pass_status = 'pass' in request.POST.getlist(f'pass_{cycle_number}')
            fail_status = 'fail' in request.POST.getlist(f'fail_{cycle_number}')
            remark = request.POST.get(f'remark_{cycle_number}')

            # Create a new run cycle entry in the database
            MachineRunTime.objects.create(
                service_report=service_report,
                run_type=f'Run cycle {cycle_number}',
                run_time=run_time,
                end_time=end_time,
                checked=checked,
                pass_status=pass_status,
                fail_status=fail_status,
                remark=remark
            )
        
        for tool in tools:
            # Get the quantity from POST data, default to 0 if invalid
            quantity_str = request.POST.get(f'quantity_{tool.id}', '')
            if not quantity_str or not quantity_str.isdigit() or int(quantity_str) < 0:
                quantity = 0  # Default to 0 if invalid
            else:
                quantity = int(quantity_str)

            # Get the remark from POST data, default to an empty string if not provided
            remark = request.POST.get(f'remark_{tool.id}', '')

            # Get the taken status from POST data, default to False if not checked
            taken_status = request.POST.get(f'taken_status_{tool.id}', '') == 'on'

            # Get or create the ToolStatus object
            tool_status, created = ToolStatus.objects.get_or_create(
            tool=tool, service_report=service_report)

            # Update the ToolStatus object with the validated values
            tool_status.quantity = quantity
            tool_status.remark = remark
            tool_status.taken_status = taken_status

            # Save the updated ToolStatus object
            tool_status.save()


            # if request.method == 'POST':
            #     state = request.POST.get('state')
        # Redirect or give feedback after saving
        # return redirect('servicereport')  # Or any other success response

    else:
        # If the request is GET, fetch all items and panels for the form
        electronic_items = ElectronicItem.objects.all()
        electronic_panels = ElectronicPanel.objects.all()
        chemical_items = ChemicalItem.objects.all()
        pumps = Pump.objects.all()
        miscellaneous_items = MiscellaneousItem.objects.all()
        wastewater_parameters = WastewaterParameter.objects.all()
        machine_runtimes=MachineRunTime.objects.all()
        states = State.objects.all()  # Get all states from the database



    context = {
        # 'service_report': service_report,
        'electronic_items': electronic_items,
        'electronic_panels': electronic_panels,
        'chemical_items': chemical_items,
        'pumps': pumps,
        'miscellaneous_items': miscellaneous_items,
        'wastewater_parameters': wastewater_parameters,
        'machine_runtimes' : machine_runtimes,
        'tools': tools,
        'states': states,


    }
    return render(request, 'servicereport.html', context)


# views.py
from django.shortcuts import render
from .models import ServiceReport

def service_report_list(request):
    search_query = request.GET.get('search', '')

    # Fetch all service reports, filtered by search query if provided
    service_reports = ServiceReport.objects.all()
    if search_query:
        service_reports = service_reports.filter(
            Q(service_name__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(state__name__icontains=search_query) |
            Q(status_of_call__icontains=search_query) |
            Q(date_of_visit__icontains=search_query)
        )

    context = {
        'service_reports': service_reports,
        'search_query': search_query,
    }
    return render(request, 'servicereport_viewing.html', context)

def view_service_report(request, pk):
    service_report = ServiceReport.objects.get(pk=pk)

    electronic_item_statuses = ElectronicItemStatus.objects.filter(report=service_report)
    panel_statuses = ElectronicPanelStatus.objects.filter(report=service_report)
    chemical_item_statuses = ChemicalItemStatus.objects.filter(report=service_report)
    pump_statuses = PumpStatus.objects.filter(report=service_report)
    miscellaneous_item_statuses = MiscellaneousItemStatus.objects.filter(report=service_report)
    wastewater_parameter_statuses = WastewaterParameterStatus.objects.filter(report=service_report)
    machine_run_times = MachineRunTime.objects.filter(service_report=service_report)
    tool_statuses = ToolStatus.objects.filter(service_report=service_report)
    context = {
        'service_report': service_report,
        'electronic_item_statuses': electronic_item_statuses,
        'panel_statuses': panel_statuses,
        'chemical_item_statuses': chemical_item_statuses,
        'pump_statuses': pump_statuses,
        'miscellaneous_item_statuses': miscellaneous_item_statuses,
        'wastewater_parameter_statuses': wastewater_parameter_statuses,
        'machine_run_times': machine_run_times,
        'tool_statuses': tool_statuses,
    }    

    return render(request, 'servicereport_detail.html', context)


import csv
from django.http import HttpResponse
import xlwt  # For XLSX export
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_service_report(request, format):
    reports = ServiceReport.objects.all()  # Adjust queryset as needed
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="service_reports.csv"'
        writer = csv.writer(response)
        writer.writerow(['Service Name', 'Date of Visit', 'Customer Name', 'State', 'Status of Call'])
        for report in reports:
            writer.writerow([report.service_name, report.date_of_visit, report.customer_name, report.state.name, report.status_of_call])
        return response

    elif format == 'xlsx':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="service_reports.xls"'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Service Reports')
        columns = ['Service Name', 'Date of Visit', 'Customer Name', 'State', 'Status of Call']
        for col_num, column in enumerate(columns):
            ws.write(0, col_num, column)
        for row_num, report in enumerate(reports, start=1):
            ws.write(row_num, 0, report.service_name)
            ws.write(row_num, 1, report.date_of_visit.strftime("%Y-%m-%d"))
            ws.write(row_num, 2, report.customer_name)
            ws.write(row_num, 3, report.state.name)
            ws.write(row_num, 4, report.status_of_call)
        wb.save(response)
        return response

    elif format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="service_reports.pdf"'
        p = canvas.Canvas(response, pagesize=letter)
        y = 750
        p.drawString(100, y, "Service Reports")
        y -= 30
        for report in reports:
            p.drawString(100, y, f"Service: {report.service_name}, Visit Date: {report.date_of_visit}, Customer: {report.customer_name}")
            y -= 20
        p.showPage()
        p.save()
        return response

    return HttpResponse("Invalid format", status=400)








