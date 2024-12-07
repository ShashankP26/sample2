from django.contrib import admin
from .models import GeneralReport

admin.site.register(GeneralReport)




# -------------------MaintenanceChecklist------------------

from django.contrib import admin
from .models import Machine, MaintenanceChecklist ,MaintenanceChecklistAttachment

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(MaintenanceChecklist)
class MaintenanceChecklistAdmin(admin.ModelAdmin):
    list_display = ('inspector_name', 'machine', 'visit_date')
    list_filter = ('date', 'machine')

@admin.register(MaintenanceChecklistAttachment)
class MaintenanceChecklistAttachmentAdmin(admin.ModelAdmin):
    list_display = ('checklist', 'file')
    search_fields = ('checklist__inspector_name', 'file')




# ---------------------GeneralReport----------------------
from django.contrib import admin
from .models import Site

# Register the Site model with the admin interface
@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display 'id' and 'name' columns in the list view
    search_fields = ('name',)  # Allow searching by 'name'

# -------------------------------MOM------------------------
from django.contrib import admin
from .models import MOM, Attachment

class MOMAdmin(admin.ModelAdmin):
    list_display = ('topic', 'organize', 'client', 'meeting_chair', 'date', 'updated_at')
    search_fields = ('topic', 'organize', 'client', 'meeting_chair')
    list_filter = ('date', 'location')

class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file', 'meeting', 'uploaded_at')
    search_fields = ('file', 'meeting__topic')

admin.site.register(MOM, MOMAdmin)
admin.site.register(Attachment, AttachmentAdmin)


# -------------------------------ServiceReport------------------------


from django.contrib import admin
from .models import ElectronicItem, ServiceReport, ElectronicItemStatus ,ElectronicPanel,ElectronicPanelStatus ,ChemicalItem ,ChemicalItemStatus
from .models import Pump, PumpStatus ,MiscellaneousItem ,MiscellaneousItemStatus ,WastewaterParameter, WastewaterParameterStatus ,MachineRunTime
from .models import ToolStatus,Tool , State
# Register ElectronicItem
@admin.register(ElectronicItem)
class ElectronicItemAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register ServiceReport
@admin.register(ServiceReport)
class ServiceReportAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'customer_name', 'date_of_visit', 'zone')
    list_filter = ('zone', 'date_of_visit', 'status_of_call')
    search_fields = ('service_name', 'customer_name', 'phone_no', 'location')

# Register ElectronicItemStatus
@admin.register(ElectronicItemStatus)
class ElectronicItemStatusAdmin(admin.ModelAdmin):
    list_display = ('report', 'item', 'checked', 'repair', 'replacement', 'remark')
    list_filter = ('checked', 'repair', 'replacement')
    search_fields = ('report__service_name', 'item__name', 'remark')

# Register ElectronicItem
@admin.register(ElectronicPanel)
class ElectronicItemAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ElectronicPanelStatus(admin.ModelAdmin):
    list_display = ('report', 'panel', 'checked', 'repair', 'replacement', 'remark')
    list_filter = ('checked', 'repair', 'replacement')
    search_fields = ('report__service_name', 'panel__name', 'remark')
# Chemical Item
@admin.register(ChemicalItem)
class ChemicalItemAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ChemicalItemStatus)
class ChemicalItemStatusAdmin(admin.ModelAdmin):
    list_display = ('report', 'item', 'checked', 'repair', 'replacement', 'remark')
    list_filter = ('checked', 'repair', 'replacement')
    search_fields = ('report__service_name', 'item__name', 'remark')
# pumps
@admin.register(Pump)
class PumpAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PumpStatus)
class PumpStatusAdmin(admin.ModelAdmin):
    list_display = ('report', 'pump', 'checked', 'repair', 'replacement', 'remark')
    list_filter = ('checked', 'repair', 'replacement')
    search_fields = ('report__service_name', 'pump__name', 'remark')
# MiscellaneousItem
@admin.register(MiscellaneousItem)
class MiscellaneousItemAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Displays the name in the list view
    search_fields = ('name',)  # Allows searching by name

@admin.register(MiscellaneousItemStatus)
class MiscellaneousItemStatusAdmin(admin.ModelAdmin):
    list_display = ('report', 'item', 'checked', 'repair', 'replacement', 'remark')
    list_filter = ('checked', 'repair', 'replacement')  # Filters for checked, repair, replacement fields
    search_fields = ('report__service_name', 'item__name', 'remark')  # Enables search by report service name, item name, and remarks

# WastewaterParameter
@admin.register(WastewaterParameter)
class WastewaterParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Displays the name in the list view
    search_fields = ('name',)  # Allows searching by name

@admin.register(WastewaterParameterStatus)
class WastewaterParameterStatusAdmin(admin.ModelAdmin):
    list_display = ('report', 'parameter', 'checked', 'repair', 'replacement', 'remark')
    list_filter = ('checked', 'repair', 'replacement')  # Filters for checked, repair, replacement fields
    search_fields = ('report__service_name', 'parameter__name', 'remark')  # Enables search by report service name, parameter name, and remarks
# MachineRunTime
@admin.register(MachineRunTime)
class MachineRunTimeAdmin(admin.ModelAdmin):
    list_display = ('run_type', 'run_time', 'end_time', 'checked', 'pass_status', 'fail_status', 'remark')
    list_filter = ('checked', 'pass_status', 'fail_status')
    search_fields = ('run_type', 'remark', 'service_report__service_name')

# toolkits

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'details')  # Fields to display in the list view
    search_fields = ('name',)  # Fields to search in the admin interface

# Register the ToolStatus model
@admin.register(ToolStatus)
class ToolStatusAdmin(admin.ModelAdmin):
    list_display = ('tool', 'service_report', 'quantity', 'remark', 'taken_status')  # Fields to display
    list_filter = ('tool', 'service_report', 'taken_status')  # Filter options
    search_fields = ('tool__name', 'service_report__id')  # Fields to search


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)