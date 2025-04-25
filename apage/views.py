from django.http import HttpResponse
from weasyprint import HTML  # WeasyPrint to generate PDF
from django.shortcuts import render, redirect ,get_object_or_404
from .models import GeneralReport


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import GeneralReport
from app.models import ModuleVisibility


def base(request):
    return render(request ,'base.html')

def home(request):
    print("apage home rendered")
    return render(request, 'apage/home.html')
def homea(request):
    return render(request, 'base_generic.html')
def  success(request):
    return render(request,'apage/success')
# -----------------------------MaintenanceChecklist-----------------------------------

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MaintenanceChecklist, Machine ,MaintenanceChecklistAttachment
from datetime import date


@login_required
def update_status(request, pk, action):
    checklist = get_object_or_404(MaintenanceChecklist, pk=pk)
    
    # if not request.user.is_staff:  # Restrict to admin users
    #     return HttpResponseForbidden("You do not have permission to perform this action.")

    if action == 'approve':
        checklist.approve()
    elif action == 'reject':
        checklist.reject()
    else:
        return HttpResponseForbidden("Invalid action.")
    
    return redirect('maintenance_checklist')  # Redirect to the checklist list page or any relevant page

def maintenance_checklist_detail(request, checklist_id):
    checklist = get_object_or_404(MaintenanceChecklist, id=checklist_id)
    attachments = checklist.attachments.all()  # Access all related attachments

    return render(request, 'apage/edithistory_maintenance.html', {
        'checklist': checklist,
        'attachments':attachments,
    })

@login_required
def maintenance_checklist_records(request):
    machines = Machine.objects.all()

    if request.method == 'POST':
        machine_id = request.POST.get('machine_name')
        visit_date = request.POST.get('visit_date')
        supply_voltage = request.POST.get('supply_voltage')
        supply_voltage_details = request.POST.get('supply_voltage_details', '')
        current_load = request.POST.get('current_load')
        current_load_details = request.POST.get('current_load_details', '')
        observations = request.POST.getlist('observation[]')  # List of observations
        attachments = request.FILES.getlist('attachment[]')  # Get multiple attachments

        # Validate required fields
        if not supply_voltage:
            return HttpResponse("Please select a supply voltage.", status=400)

        if not current_load:
            return HttpResponse("Please select a current load.", status=400)

        # Capture the current date when the form is submitted
        current_date = date.today()

        try:
            machine = Machine.objects.get(id=machine_id)
        except Machine.DoesNotExist:
            return HttpResponse("Machine not found.", status=404)

        # Concatenate observations into a single string if needed
        observations_text = "\n".join(observations)

        # Create the Maintenance Checklist entry with individual fields
        checklist = MaintenanceChecklist(
            inspector_name=request.user.username,  # Auto-fill with logged-in user's username
            machine=machine,
            visit_date=visit_date,
            supply_voltage=supply_voltage,  # Store directly in the supply_voltage field
            current_load=current_load,  # Store directly in the current_load field
            observations=observations_text,  # Store observations in the observations field
            date=current_date,  # Store the current date
            created_by=request.user
        )
        checklist.save()
        checklist.full_clean()

        # Save each uploaded attachment
        for attachment in attachments:
            MaintenanceChecklistAttachment.objects.create(checklist=checklist, file=attachment)

        # Redirect after successful save (customize as needed)
        return redirect('maintenance_checklist')  # Adjust this to your URL name

    return render(request, 'apage/maintenance_checklist.html', {'machines': machines})





from django.shortcuts import render
from .models import MaintenanceChecklist
# maintenance_checklist_records

def maintenance_checklist(request):
    user = request.user
    checklists = MaintenanceChecklist.objects.filter(created_by=user).order_by('-date')  # Order by most recent
    query = request.GET.get('search', '')
    if query:
        checklists = checklists.filter(
            # Q(inspector_name__icontains=query) |
                Q(date__icontains=query) |
                Q(machine__name__icontains=query) |
                Q(visit_date__icontains=query) |
                Q(observations__icontains=query)
        )

    context = {
        'checklists': checklists,
        'search_query': query,
    }
    return render(request, 'apage/maintenance_checklist_viewing.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import MaintenanceChecklist, Machine, MaintenanceChecklistAttachment

def edit_maintenance_checklist(request, id):
    # Get the checklist record or return 404 if not found
    checklist = get_object_or_404(MaintenanceChecklist, id=id)

    if request.method == 'POST':
        # Update checklist fields
        checklist.inspector_name = request.POST.get('inspector_name', checklist.inspector_name)
        checklist.date = request.POST.get('date', checklist.date)
        checklist.visit_date = request.POST.get('visit_date', checklist.visit_date)

        # Handle supply_voltage (checkboxes)
        checklist.supply_voltage = request.POST.getlist('supply_voltage')  # This will return a list of selected values
        checklist.supply_voltage_details = request.POST.get('supply_voltage_details', checklist.supply_voltage)

        # Handle current_load (checkboxes)
        checklist.current_load = request.POST.getlist('current_load')  # This will return a list of selected values
        checklist.current_load_details = request.POST.get('current_load_details', checklist.current_load)

        # Handle observations (array of observations)
        observations = request.POST.getlist('observation[]')  # This retrieves a list of observations
        checklist.observations = '\n'.join(observations)  # Join them with a newline for easy readability

        for attachment in checklist.attachments.all():
            remove_key = f"remove_attachment_{attachment.id}"
            if remove_key in request.POST:
                attachment.delete()


        # Update the machine field if provided
        machine_id = request.POST.get('machine_name')
        if machine_id:
            checklist.machine = get_object_or_404(Machine, id=machine_id)

        checklist.save()

        # Handle the uploaded attachments
        files = request.FILES.getlist('attachment[]')  # Make sure this matches the form input name
        for file in files:
            MaintenanceChecklistAttachment.objects.create(checklist=checklist, file=file)

        # Redirect to the maintenance checklist records page
        return redirect('maintenance_checklist')

    # Fetch machines and existing attachments
    machines = Machine.objects.all()
    attachments = checklist.attachments.all()  # Correctly fetch attachments using `related_name`

    # Render the edit page with all required data
    return render(request, 'apage/edit_maintenance_checklist.html', {
        'checklist': checklist,
        'machines': machines,
        'attachments': attachments,
        'supply_voltage': checklist.supply_voltage,
        'current_load': checklist.current_load,
        'observations': checklist.observations,
    })

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import MaintenanceChecklist

def pdf_maintenance_checklist(request, checklist_id):
    # Fetch the checklist record by ID
    checklist = get_object_or_404(MaintenanceChecklist, pk=checklist_id)

    # Render the HTML template for the checklist
    html_content = render_to_string('apage/pdf_maintenance_checklist.html', {'checklist': checklist})

    # Convert HTML to PDF using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()

    # Return the PDF response as a downloadable file
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=maintenance_checklist_{checklist.id}.pdf'
    return response




# -----------------------------MOM-----------------------------------


def mom_details_with_history(request, mom_id):
    # Retrieve the MOM instance
    mom = get_object_or_404(MOM, id=mom_id)

    # Render the details and history
    return render(request, 'apage/edithistory_mom.html', {'mom': mom})

from django.shortcuts import render, redirect
from .models import MOM, Attachment
from django.utils.timezone import now

def mom(request):
    # Fetch all MOM records ordered by the most recent
    mom_records = MOM.objects.filter(created_by=request.user).order_by('-id')  # Adjust the order as needed
    search_query = request.GET.get('search', '')
    if search_query:
        mom_records = mom_records.filter(
            Q(topic__icontains=search_query) |
            Q(organize__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(meeting_chair__icontains=search_query) |
            Q(date__icontains=search_query)
        )

    context = {
        'mom_records': mom_records,
        'search_query': search_query,
    }
    return render(request, 'apage/mom_viewing.html', context)
    


from django.shortcuts import render, redirect
from .models import MOM, Attachment
@login_required
def mom_new(request):
    if request.method == 'POST':
        # Create the meeting instance from POST data
        meeting = MOM(
            topic=request.POST['topic'],
            organize=request.POST['organize'],
            meeting_chair=request.POST['meeting_chair'],
            location=request.POST['location'],
            date=request.POST['mdate'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            duration=request.POST['duration'],
            updated_by=request.user.username,  # Set logged-in user as the updater
            meeting_conclusion=request.POST['meeting_conclusion'],
            summary_of_discussion=request.POST['summary_of_discussion'],
            attendees=request.POST.getlist('attendees[]'),
            apologies=request.POST.getlist('apologies[]'),
            agenda=request.POST.getlist('agenda[]'),
            created_by=request.user
        )

        # Save the meeting instance to the database

        meeting.save()
        meeting.full_clean()

        # Save the uploaded files (attachments)
        for attachment_file in request.FILES.getlist('attachment[]'):
            attachment = Attachment(file=attachment_file, meeting=meeting)
            attachment.save()

        # Redirect to the mom_viewing page with the newly created meeting's ID
        return redirect('mom')

    # If the request is not POST, render the form page
    return render(request, 'apage/mom.html')

    

def mom_detail(request, mom_id):
    mom = get_object_or_404(MOM, id=mom_id)
    return render(request, 'apage/mom_detail.html', {'mom': mom})

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import MOM, Attachment

def mom_edit(request, mom_id):
    # Fetch the MOM record to be edited
    mom = get_object_or_404(MOM, id=mom_id)
    print(f"dr,{mom.duration}")
    if request.method == 'POST':
        # Update the meeting instance with the new data from POST
        mom.topic = request.POST['topic']
        mom.organize = request.POST['organize']
        mom.meeting_chair = request.POST['meeting_chair']
        mom.location = request.POST['location']
        mom.date = request.POST['mdate']
        mom.start_time = request.POST['start_time']
        mom.end_time = request.POST['end_time']
        mom.duration = request.POST['duration']
        mom.updated_by = request.user.username  # Set the logged-in user as the updater
        mom.meeting_conclusion = request.POST['meeting_conclusion']
        mom.summary_of_discussion = request.POST['summary_of_discussion']
        mom.attendees = request.POST.getlist('attendees[]')
        mom.apologies = request.POST.getlist('apologies[]')
        mom.agenda = request.POST.getlist('agenda[]')

        # Save the updated meeting instance
        mom.save()

        # Handle file attachments
        for attachment_file in request.FILES.getlist('attachment[]'):
            attachment = Attachment(file=attachment_file, meeting=mom)
            attachment.save()

        # Redirect to the MOM detail page after saving the changes
        return redirect('mom_detail', mom_id=mom.id)

    # If the request is not POST, display the edit form with existing data
    return render(request, 'apage/edit_mom.html', {'mom': mom})


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML

def pdf_mom(request, mom_id):
    # Fetch the MOM record by ID
    mom = get_object_or_404(MOM, pk=mom_id)

    # Render the HTML content to be converted to PDF
    html_content = render_to_string('apage/pdf_mom.html', {'mom': mom})

    # Convert HTML to PDF using WeasyPrint
    pdf = HTML(string=html_content).write_pdf()

    # Return the PDF response as a downloadable file
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=mom_{mom.id}.pdf'
    return response




# --------------------------generalreport-----------------------------

from django.shortcuts import render, redirect
from .models import GeneralReport, Site
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from .models import Site, GeneralReport
from django.shortcuts import render, get_object_or_404

def view_edit_history(request, report_id):
    report = get_object_or_404(GeneralReport, id=report_id)
    return render(request, 'apage/edithistory_generalreport.html', {'report': report})

@login_required
def generalreportsnew(request):
    sites = Site.objects.all()  # Get all available sites
    if request.method == 'POST':
        # Fetch the Site instance by ID from the POST data
        site_id = request.POST.get('site')
        try:
            site_instance = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return render(request, 'apage/error_template.html', {'error': 'Invalid site selected'})

        # Create a GeneralReport instance without saving to the database
        report = GeneralReport(
            site=site_instance,
            date_of_visit=request.POST.get('date_of_visit'),
            point1=request.POST.get('point1'),
            point2=request.POST.get('point2'),
            point3=request.POST.get('point3'),
            point4=request.POST.get('point4'),
            notes=request.POST.get('notes'),
            attachment=request.FILES.get('attachment'),
            created_by=request.user
        )

        # Validate the report instance
        try:
            report.full_clean()  # This triggers the no_future_dates validator
            report.save()  # Save only if validation passes
        except ValidationError as e:
            # If validation fails, re-render the form with errors
            return render(request, 'apage/generalreport.html', {
                'reports': GeneralReport.objects.all(),
                'sites': sites,
                'error': e.message_dict  # Pass validation error messages to the template
            })

        # Redirect to the viewing page after successful save
        return redirect('generalreport')  # Ensure this URL name is correct

    # Fetch all saved reports to display
    reports = GeneralReport.objects.all()
    return render(request, 'apage/generalreport.html', {'reports': reports, 'sites': sites})



from django.db.models import Q

def generalreport(request):
    query = request.GET.get('search', '')
    reports = GeneralReport.objects.filter(created_by=request.user).order_by('-id')



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
    return render(request, 'apage/generalreportviewing.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from .models import GeneralReport, Site

def edit_general_report(request, report_id):
    report = get_object_or_404(GeneralReport, id=report_id)
    sites = Site.objects.all()  # For the site selection dropdown

    if request.method == 'POST':
        # Fetch the updated data from the form
        site_id = request.POST.get('site')
        try:
            site_instance = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return render(request, 'apage/error_template.html', {'error': 'Invalid site selected'})

        # Update the GeneralReport instance
        report.site = site_instance
        report.date_of_visit = request.POST.get('date_of_visit')
        report.point1 = request.POST.get('point1')
        report.point2 = request.POST.get('point2')
        report.point3 = request.POST.get('point3')
        report.point4 = request.POST.get('point4')
        report.notes = request.POST.get('notes')

        # Update attachment if a new file is uploaded
        if request.FILES.get('attachment'):
            report.attachment = request.FILES.get('attachment')
        report.full_clean() 
        report.save()  # Save the updated report

        return redirect('generalreport')  # Redirect to the report list page

    return render(request, 'apage/edit_general_report.html', {'report': report, 'sites': sites})


from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from weasyprint import HTML
from .models import GeneralReport

def generate_report_pdf(request, report_id):
    # Fetch the report based on its ID
    report = get_object_or_404(GeneralReport, pk=report_id)

    # Create the HTML content to be converted to PDF
    html_content = render(request, 'apage/pdf_generalreport.html', {'report': report})

    # Convert HTML to PDF using WeasyPrint
    pdf = HTML(string=html_content.content.decode('utf-8')).write_pdf()

    # Return the PDF response as a downloadable file
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=general_report_{report.id}.pdf'
    return response


# ------------servicereport--------------------

from django.shortcuts import render, redirect
from .models import ServiceReport, ElectronicItem, ElectronicItemStatus, ElectronicPanel ,ElectronicPanelStatus ,WastewaterParameterStatus
from .models import ChemicalItem ,ChemicalItemStatus ,Pump ,PumpStatus ,MiscellaneousItem ,MiscellaneousItemStatus ,WastewaterParameter
from .models import MachineRunTime ,Tool ,ToolStatus ,State
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def servicereport(request):
    search_query = request.GET.get('search', '')

    # Filter service reports based on the logged-in user's name
    service_reports = ServiceReport.objects.filter(created_by=request.user).order_by('-id')
    
    # Apply additional filtering if a search query is provided
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
    return render(request, 'apage/servicereport_viewing.html', context)

# views.py
from django.shortcuts import render
from .models import ServiceReport

def service_report_new(request):
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
        service_person_signature = request.POST.get('service_person_signature', '')
        service_person_name = request.POST.get('service_person_name', '')
        client_signature = request.POST.get('client_signature', '')
        client_name = request.POST.get('client_name', '')
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
            status_of_call=status_of_call,
            service_person_signature=service_person_signature,
            service_person_name=service_person_name,
            client_signature=client_signature,
            client_name=client_name,
            created_by=request.user
            
        )

        electronic_panels = ElectronicPanel.objects.all()
        electronic_items = ElectronicItem.objects.all()
        chemical_items = ChemicalItem.objects.all()
        pumps = Pump.objects.all()
        miscellaneous_items = MiscellaneousItem.objects.all()
        wastewater_parameters = WastewaterParameter.objects.all()
        machine_runtimes =MachineRunTime.objects.all()
        states = State.objects.all()  # Get all states from the database
        remarks = []
        spares = []
        # Collect all remarks from form data
        for key, value in request.POST.items():
            if key.startswith('remark_orm_') and value.strip():
                remarks.append(value.strip())
                # Collect spares details
        for key, value in request.POST.items():
            if key.startswith('spare_') and value.strip():
                spares.append(value.strip())


        # Join all remarks into a single string separated by newlines
        service_report.other_remarks = '\n'.join(remarks)
        service_report.spares_details = '\n'.join(spares)
        service_report.full_clean() 
        service_report.save()     
        # Handle dynamic electronic items and their statuses
        for item in electronic_items:
            checked = request.POST.get(f'checked_{item.id}') == 'on'
            repair = request.POST.get(f'repair_{item.id}') == 'on'
            replacement = request.POST.get(f'replacement_{item.id}') == 'on'
            remark = request.POST.get(f'remark_eitems_{item.id}')

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
            remark = request.POST.get(f'remark_epanels_{panel.id}')

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
        

        #Machine Run Time.
        run_cycle_count = int(request.POST.get('run_cycle_count', 1))
        rc = run_cycle_count+1
        for cycle_number in range(1, rc):
            print(cycle_number)
            # Get data for each cycle (this assumes you have added the fields for each run cycle)
            run_time = request.POST.get(f'run_time_{cycle_number}')
            end_time = request.POST.get(f'end_time_{cycle_number}')
            if not run_time or not end_time:
                continue  
            checked =request.POST.get(f'checked_run_{cycle_number}') == "on"
            pass_status =request.POST.get(f'pass_run_{cycle_number}') == "on"
            fail_status = request.POST.get(f'fail_run_{cycle_number}') == "on"
            remark = request.POST.get(f'remark_run_{cycle_number}')

            print(f"Cycle {cycle_number}: {run_time}, {end_time}, {checked}, {pass_status}, {fail_status}, {remark}")
            


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
            remark = request.POST.get(f'remark_tools_{tool.id}', '')

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
            return redirect('servicereport')


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
    return render(request, 'apage/servicereport.html', context)


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

    return render(request, 'apage/servicereport_detail.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    ServiceReport,
    ElectronicItemStatus,
    ElectronicPanelStatus,
    ChemicalItemStatus,
    PumpStatus,
    MiscellaneousItemStatus,
    WastewaterParameterStatus,
    MachineRunTime,
    ToolStatus,
)
from django.shortcuts import render, get_object_or_404, redirect
from .models import ServiceReport, State, ElectronicItemStatus, ElectronicPanelStatus, ChemicalItemStatus, PumpStatus, MiscellaneousItemStatus, WastewaterParameterStatus, MachineRunTime, ToolStatus

def edit_service_report(request, report_id):
    # Fetch the service report that needs to be edited
    service_report = get_object_or_404(ServiceReport, id=report_id)

    # Fetch related data for the form (filtering by the service report)
    electronic_items = ElectronicItemStatus.objects.filter(report=service_report)
    electronic_panels = ElectronicPanelStatus.objects.filter(report=service_report)
    chemical_items = ChemicalItemStatus.objects.filter(report=service_report)
    pumps = PumpStatus.objects.filter(report=service_report)
    miscellaneous_items = MiscellaneousItemStatus.objects.filter(report=service_report)
    wastewater_parameters = WastewaterParameterStatus.objects.filter(report=service_report)
    machine_runs = MachineRunTime.objects.filter(service_report=service_report)
    tools = ToolStatus.objects.filter(service_report=service_report)
    states = State.objects.all()  # For the dropdown in the form
    service_report.edited_by = request.user
    if request.method == 'POST':
        # Process form data
        state_id = request.POST.get('state')  # Get state from the form
        
        if state_id:
            try:
                # Try to fetch the state by ID (as that's usually passed from the form)
                state_instance = State.objects.get(id=state_id)
                service_report.state = state_instance  # Assign the correct state instance
            except State.DoesNotExist:
                print(f"State with ID {state_id} does not exist.")
        else:
            print("No state was selected or passed.")

        # Other fields assignment from the form
        service_report.date_of_visit = request.POST.get('date_of_visit')
        service_report.zone = request.POST.get('zone')
        service_report.phone_no = request.POST.get('phone_no')
        service_report.reason_of_visit = request.POST.get('reason_of_visit')
        service_report.in_time = request.POST.get('in_time')
        service_report.out_time = request.POST.get('out_time')
        service_report.customer_name = request.POST.get('customer_name')
        service_report.contact_number = request.POST.get('contact_number')
        service_report.location = request.POST.get('location')
        service_report.date_of_complaint = request.POST.get('date_of_complaint')
        service_report.status_of_call = request.POST.get('status_of_call')
        # Updating signatures and names
        service_report.service_person_name = request.POST.get('service_person_name', service_report.service_person_name)
        service_report.client_name = request.POST.get('client_name', service_report.client_name)
        
        # Handle the service person signature (base64 data)
        service_person_signature = request.POST.get('service_person_signature')
        if service_person_signature:
            service_report.service_person_signature = service_person_signature

        # Handle the client signature (base64 data)
        client_signature = request.POST.get('client_signature')
        if client_signature:
            service_report.client_signature = client_signature

        # Handle the remarks and spare details
        remarks = []
        spares = []
        
        # Collect all remarks from form data
        for key, value in request.POST.items():
            if key.startswith('remark_orm_') and value.strip():
                remarks.append(value.strip())

        # Collect all spares from form data
        for key, value in request.POST.items():
            if key.startswith('spare_') and value.strip():
                spares.append(value.strip())

        # Join all remarks and spares into a single string separated by newlines
        service_report.other_remarks = '\n'.join(remarks)
        service_report.spares_details = '\n'.join(spares)
        service_report.user = request.user
        # Save the service report
        service_report.save()

        # Save dynamic items (Electronic, Chemical, Pump, Miscellaneous, etc.)
        for item in electronic_items:
            item.checked = 'checked_' + str(item.id) in request.POST
            item.repair = 'repair_' + str(item.id) in request.POST
            item.replacement = 'replacement_' + str(item.id) in request.POST
            item.remark = request.POST.get('remark_epanels_' + str(item.id), '')
            item.save()

        for item in electronic_panels:
            item.checked = 'checked_' + str(item.id) in request.POST
            item.repair = 'repair_' + str(item.id) in request.POST
            item.replacement = 'replacement_' + str(item.id) in request.POST
            item.remark = request.POST.get('remark_eitems_' + str(item.id), '')
            item.save()

        for item in chemical_items:
            item.checked = 'checked_chemical_' + str(item.id) in request.POST
            item.repair = 'repair_chemical_' + str(item.id) in request.POST
            item.replacement = 'replacement_chemical_' + str(item.id) in request.POST
            item.remark = request.POST.get('remark_chemical_' + str(item.id), '')
            item.save()

        for pump in pumps:
            pump.checked = 'checked_pump_' + str(pump.id) in request.POST
            pump.repair = 'repair_pump_' + str(pump.id) in request.POST
            pump.replacement = 'replacement_pump_' + str(pump.id) in request.POST
            pump.remark = request.POST.get('remark_pump_' + str(pump.id), '')
            pump.save()

        for item in miscellaneous_items:
            item.checked = 'checked_miscellaneous_' + str(item.id) in request.POST
            item.repair = 'repair_miscellaneous_' + str(item.id) in request.POST
            item.replacement = 'replacement_miscellaneous_' + str(item.id) in request.POST
            item.remark = request.POST.get('remark_miscellaneous_' + str(item.id), '')
            item.save()

        for parameter in wastewater_parameters:
            parameter.checked = 'checked_wastewater_' + str(parameter.id) in request.POST
            parameter.repair = 'repair_wastewater_' + str(parameter.id) in request.POST
            parameter.replacement = 'replacement_wastewater_' + str(parameter.id) in request.POST
            parameter.remark = request.POST.get('remark_wastewater_' + str(parameter.id), '')
            parameter.save()

        for run in machine_runs:
            run.run_time = request.POST.get('run_time_' + str(run.id), '')
            run.end_time = request.POST.get('end_time_' + str(run.id), '')
            run.checked = 'checked_run_' + str(run.id) in request.POST
            run.pass_ = 'pass_run_' + str(run.id) in request.POST
            run.fail = 'fail_run_' + str(run.id) in request.POST
            run.remark = request.POST.get('remark_run_' + str(run.id), '')
            run.save()

        for tool in tools:
            tool.quantity = request.POST.get('quantity_' + str(tool.id), '')
            tool.remark = request.POST.get('remark_tools_' + str(tool.id), '')
            tool.taken_status = 'taken_status_' + str(tool.id) in request.POST
            tool.save()

        # Redirect or show success message
        return redirect('view_service_report', pk=service_report.id)

    # Display the form with current values
    return render(request, 'apage/edit_service_report.html', {
        'service_report': service_report,
        'electronic_items': electronic_items,
        'electronic_panels': electronic_panels,
        'chemical_items': chemical_items,
        'pumps': pumps,
        'miscellaneous_items': miscellaneous_items,
        'wastewater_parameters': wastewater_parameters,
        'machine_runs': machine_runs,
        'tools': tools,
        'states': states,  # Provide the states to the template
    })

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from .models import (
    ServiceReport,
    ElectronicItemStatus,
    ElectronicPanelStatus,
    ChemicalItemStatus,
    PumpStatus,
    MiscellaneousItemStatus,
    WastewaterParameterStatus,
    MachineRunTime,
    ToolStatus,
    State,
)

def service_report_pdf(request, pk):
    service_report = ServiceReport.objects.get(pk=pk)
    electronic_item_statuses = ElectronicItemStatus.objects.filter(report=service_report)
    panel_statuses = ElectronicPanelStatus.objects.filter(report=service_report)
    chemical_item_statuses = ChemicalItemStatus.objects.filter(report=service_report)
    pump_statuses = PumpStatus.objects.filter(report=service_report)
    miscellaneous_item_statuses = MiscellaneousItemStatus.objects.filter(report=service_report)
    wastewater_parameter_statuses = WastewaterParameterStatus.objects.filter(report=service_report)
    machine_run_times = MachineRunTime.objects.filter(service_report=service_report)
    tool_statuses = ToolStatus.objects.filter(service_report=service_report)

    # Prepare context for the template
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

    # Render the HTML template as a string
    html_string = render_to_string('apage/pdf_servicereport.html', context)

    try:
        # Generate the PDF using WeasyPrint
        pdf_file = HTML(string=html_string).write_pdf()
    except Exception as e:
        # Return a plain text error if PDF generation fails
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)

    # Return the PDF as a response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="service_report_{pk}.pdf"'
    return response



from django.shortcuts import render
from .models import ServiceReport, ServiceReportEditLog, ElectronicItemStatus, ElectronicPanelStatus, ChemicalItemStatus, PumpStatus, MiscellaneousItemStatus, WastewaterParameterStatus, MachineRunTime, ToolStatus

def servireport_edithistory(request, report_id):
    # Get the specific ServiceReport
    service_report = ServiceReport.objects.get(id=report_id)

    # Get the edit logs for this report
    edit_logs = ServiceReportEditLog.objects.filter(report=service_report).order_by('-edit_timestamp')
    service_report.user = request.user

    # Get the related statuses and data for the report
    electronic_item_statuses = ElectronicItemStatus.objects.filter(report=service_report)
    panel_statuses = ElectronicPanelStatus.objects.filter(report=service_report)
    chemical_item_statuses = ChemicalItemStatus.objects.filter(report=service_report)
    pump_statuses = PumpStatus.objects.filter(report=service_report)
    miscellaneous_item_statuses = MiscellaneousItemStatus.objects.filter(report=service_report)
    wastewater_parameter_statuses = WastewaterParameterStatus.objects.filter(report=service_report)
    machine_run_times = MachineRunTime.objects.filter(service_report=service_report)
    tool_statuses = ToolStatus.objects.filter(service_report=service_report)

    # Pass all the necessary data to the template
    context = {
        'service_report': service_report,
        'edit_logs': edit_logs,
        'electronic_item_statuses': electronic_item_statuses,
        'panel_statuses': panel_statuses,
        'chemical_item_statuses': chemical_item_statuses,
        'pump_statuses': pump_statuses,
        'miscellaneous_item_statuses': miscellaneous_item_statuses,
        'wastewater_parameter_statuses': wastewater_parameter_statuses,
        'machine_run_times': machine_run_times,
        'tool_statuses': tool_statuses,
    }

    return render(request, 'apage/edithistory_servicereport.html', context)

@login_required
def update_service_report_status(request, pk, action):
    service_report = get_object_or_404(ServiceReport, pk=pk)

    # Ensure the action is valid
    if action == 'approve':
        service_report.approve()  # Calls the approve method from the model to update status
    elif action == 'reject':
        service_report.reject()  # Calls the reject method from the model to update status
    else:
        return HttpResponseForbidden("Invalid action.")  # If action is not approve or reject

    # Redirect to the service report list or any other relevant page after action
    return redirect('servicereport')  # Adjust URL as per your project’s structure

# ---------------------------------dashboard----------------------

from django.shortcuts import render
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

from .models import ServiceReport, MOM, MaintenanceChecklist, GeneralReport

def dashboard(request):
    today = timezone.now().date()

    # Default to current month
    start_date = today.replace(day=1)

    # Get the selected time range from the query parameters (defaults to 'month')
    time_range = request.GET.get('time_range', 'month')

    if time_range == 'week':
        # Start date for the last week (7 days ago)
        start_date = today - timedelta(days=7)
    elif time_range == 'month':
        # Start date for the current month (1st day of this month)
        start_date = today.replace(day=1)
    elif time_range == '60_days':
        # Start date for the last 60 days
        start_date = today - timedelta(days=60)
    elif time_range == '3_months':
        # Start date for the last 3 months (approx. 90 days)
        start_date = today - timedelta(days=90)
    elif time_range == '6_months':
        # Start date for the last 6 months (approx. 180 days)
        start_date = today - timedelta(days=180)
    elif time_range == '1_year':
        # Start date for the last 1 year (approx. 365 days)
        start_date = today - timedelta(days=365)

    # Aggregates for selected time range
    # Check user role and filter reports
    user = request.user
    print(user)
    user_role = user.groups.first().name if user.groups.exists() else None
    completeion = request.GET.get('status', 'all')


    if user_role == "admin":
        # Admin users can see all reports
        service_reports = ServiceReport.objects.filter(created_date__gte=start_date)
        mom_reports = MOM.objects.filter(created_date__gte=start_date)
        maintenance_reports = MaintenanceChecklist.objects.filter(date__gte=start_date)
        general_reports = GeneralReport.objects.filter(created_date__gte=start_date)
    else:
        # Non-admin users can only see their reports
        service_reports = ServiceReport.objects.filter(created_by=request.user, created_date__gte=start_date)
        mom_reports = MOM.objects.filter(created_by=request.user, created_date__gte=start_date)
        maintenance_reports = MaintenanceChecklist.objects.filter(created_by=request.user, date__gte=start_date)
        general_reports = GeneralReport.objects.filter(created_by=request.user, created_date__gte=start_date)

     # Apply status filter
    if completeion != 'all':
        service_reports = service_reports.filter(status=completeion)
        maintenance_reports = maintenance_reports.filter(status=completeion)

    months_in_range = ((today.year - start_date.year) * 12 + today.month - start_date.month) + 1
    required_service_reports = 2 * months_in_range
    required_maintenance_checklists = 4 * months_in_range

    total_service_reports = service_reports.count()
    total_maintenance_reports = maintenance_reports.count()

    service_compliance = min(total_service_reports / required_service_reports, 1) *100
    if total_maintenance_reports > required_maintenance_checklists:
        maintenance_compliance = max(total_maintenance_reports / required_maintenance_checklists, 1) *100
    else :
        maintenance_compliance =min(total_maintenance_reports / required_maintenance_checklists, 1) *100
    service_submitted = total_service_reports
    service_remaining = max(0, required_service_reports - total_service_reports)

    maintenance_submitted = total_maintenance_reports
    maintenance_remaining = max(0, required_maintenance_checklists - total_maintenance_reports)

    compliance_status = {
        'service': {
            'compliance': service_compliance,
            'status': "green" if service_compliance == 100 else ("yellow" if service_compliance < 100 else "blue"),
        },
        'maintenance': {
            'compliance': maintenance_compliance,
            'status': "blue" if maintenance_compliance > 100 else ("yellow" if maintenance_compliance < 100 else "green"),
        }
    }
    print(compliance_status)
    print(completeion)

    # Total count for each report type for selected time range
    total_service_reports = service_reports.count()
    total_mom_reports = mom_reports.count()
    total_maintenance_reports = maintenance_reports.count()
    total_general_reports = general_reports.count()

    # Context to pass to the template
    context = {
        'service_reports': service_reports,
        'mom_reports': mom_reports,
        'maintenance_reports': maintenance_reports,
        'general_reports': general_reports,
        'total_service_reports': total_service_reports,
        'total_mom_reports': total_mom_reports,
        'total_maintenance_reports': total_maintenance_reports,
        'total_general_reports': total_general_reports,
        'time_range': time_range,
        'compliance_status': compliance_status,
        'service_submitted': service_submitted,
        'service_remaining': service_remaining,
        'maintenance_submitted': maintenance_submitted,
        'maintenance_remaining': maintenance_remaining,
        'status_filter':completeion,
    }
    return render(request, 'apage/dashboard.html', context)



    


