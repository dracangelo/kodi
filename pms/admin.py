from django.contrib import admin
from .models import Property, Unit, Tenant, Lease, Payment, Expense, MaintenanceTicket, Visitor

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'owner', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'address')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'property', 'unit_type', 'rent_amount', 'status')
    list_filter = ('status', 'unit_type', 'property')
    search_fields = ('unit_number',)

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'id_passport_number', 'status')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name', 'id_passport_number')

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'unit', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'tenant', 'amount', 'date', 'method')
    list_filter = ('method', 'date')
    search_fields = ('receipt_number',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('category', 'property', 'amount', 'date')
    list_filter = ('category', 'property', 'date')

@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'unit', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'category')
    search_fields = ('description',)

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_visiting', 'entry_time', 'exit_time')
    list_filter = ('entry_time',)
    search_fields = ('name', 'phone', 'vehicle_plate')
