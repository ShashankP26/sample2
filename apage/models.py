from django.db import models

class Site(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class GeneralReport(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    date_of_visit = models.DateField()
    point1 = models.TextField()
    point2 = models.TextField()
    point3 = models.TextField()
    point4 = models.TextField()
    notes = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)

    def __str__(self):
        return f"Report for {self.site.name} on {self.date_of_visit}"




# -----------------------------MaintenanceChecklist-----------------------------------
class Machine(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MaintenanceChecklist(models.Model):
    inspector_name = models.CharField(max_length=255, null=True, blank=True)  # Auto-filled by logged-in user
    date = models.DateField()  # Stores the current date
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    visit_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.inspector_name} - {self.machine.name} on {self.visit_date}"
    
class MaintenanceChecklistAttachment(models.Model):
    checklist = models.ForeignKey(MaintenanceChecklist, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')

    
# ----------------------------------------mom---------------------------------
from django.db import models

class MOM(models.Model):
    topic = models.CharField(max_length=255)
    organize = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    meeting_chair = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.CharField(max_length=255, blank=True)
    updated_by = models.CharField(max_length=255)
    meeting_conclusion = models.TextField()
    summary_of_discussion = models.TextField()
    attendees = models.JSONField(default=list)
    apologies = models.JSONField(default=list)
    agenda = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.topic

class Attachment(models.Model):
    file = models.FileField(upload_to='meetings/attachments/')
    meeting = models.ForeignKey(MOM, related_name='attachments', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


# --------------------------------service report ----------------------


from django.db import models

class ElectronicItem(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class ElectronicPanel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class ChemicalItem(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Pump(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class MiscellaneousItem(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class WastewaterParameter(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
# --------------------------------------------------------------------------

class State(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class ServiceReport(models.Model):
    # Static fields
    service_name = models.CharField(max_length=255)
    date_of_visit = models.DateField()
    zone = models.CharField(max_length=100, choices=[('G', 'GKN'), ('C', 'CHP'), ('S', 'SRS')])
    phone_no = models.CharField(max_length=15)
    reason_of_visit = models.CharField(max_length=255)
    in_time = models.TimeField()
    out_time = models.TimeField()
    other_remarks = models.TextField(blank=True, null=True, help_text="Store all other remarks concatenated.")
    spares_details = models.TextField(blank=True, null=True, help_text="Concatenated spares details")
    certified_by = models.CharField(max_length=255, blank=True, null=True)
    certified_by_name = models.CharField(max_length=255, blank=True, null=True)

    # Customer Information
    customer_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    date_of_complaint = models.DateField()
    status_of_call = models.CharField(max_length=100)

    # Dynamic Fields for Electronic Items
    electronic_items = models.ManyToManyField(ElectronicItem, through='ElectronicItemStatus')
    electronic_panels = models.ManyToManyField(ElectronicPanel, through='ElectronicPanelStatus')
    chemical_items = models.ManyToManyField(ChemicalItem, through='ChemicalItemStatus')
    pumps = models.ManyToManyField(Pump, through='PumpStatus')
    miscellaneous_items = models.ManyToManyField(MiscellaneousItem, through='MiscellaneousItemStatus')
    wastewater_parameters = models.ManyToManyField(WastewaterParameter, through='WastewaterParameterStatus')


    def __str__(self):
        return f"Service Report for {self.service_name} - {self.customer_name}"

    class Meta:
        verbose_name = 'Service Report'
        verbose_name_plural = 'Service Reports'


class ElectronicItemStatus(models.Model):
    report = models.ForeignKey(ServiceReport, on_delete=models.CASCADE)
    item = models.ForeignKey(ElectronicItem, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)
    repair = models.BooleanField(default=False)
    replacement = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)

class ElectronicPanelStatus(models.Model):
    report = models.ForeignKey(ServiceReport, on_delete=models.CASCADE)
    panel = models.ForeignKey(ElectronicPanel, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)
    repair = models.BooleanField(default=False)
    replacement = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.report} - {self.panel.name}"

class ChemicalItemStatus(models.Model):
    report = models.ForeignKey(ServiceReport, on_delete=models.CASCADE)
    item = models.ForeignKey(ChemicalItem, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)
    repair = models.BooleanField(default=False)
    replacement = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.report} - {self.item.name}"
class PumpStatus(models.Model):
    report = models.ForeignKey(ServiceReport, on_delete=models.CASCADE)
    pump = models.ForeignKey(Pump, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)
    repair = models.BooleanField(default=False)
    replacement = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.report} - {self.pump.name}"

class MiscellaneousItemStatus(models.Model):
    report = models.ForeignKey(ServiceReport, on_delete=models.CASCADE)
    item = models.ForeignKey(MiscellaneousItem, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)
    repair = models.BooleanField(default=False)
    replacement = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.report} - {self.item.name}"

class WastewaterParameterStatus(models.Model):
    report = models.ForeignKey(ServiceReport, on_delete=models.CASCADE)
    parameter = models.ForeignKey(WastewaterParameter, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)
    repair = models.BooleanField(default=False)
    replacement = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.report} - {self.parameter.name}"
    
class MachineRunTime(models.Model):
    service_report = models.ForeignKey(ServiceReport, related_name='run_times', on_delete=models.CASCADE)
    run_type = models.CharField(max_length=255)  # Example: Run cycle 1, Run cycle 2, etc.
    run_time = models.TimeField()
    end_time = models.TimeField()
    checked = models.BooleanField(default=False)
    pass_status = models.BooleanField(default=False)
    fail_status = models.BooleanField(default=False)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.run_type} - {self.run_time} to {self.end_time}'
    

class Tool(models.Model):
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=255, blank=True, null=True ,default='')

    def __str__(self):
        return self.name

class ToolStatus(models.Model):
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    service_report = models.ForeignKey('ServiceReport', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, null=False, blank=False)
    remark = models.TextField(blank=True, null=True)
    taken_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tool.name} - {self.service_report.id}"
