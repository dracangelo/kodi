from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, Q
from .models import Property, Unit, Tenant, Lease, Payment, Expense, MaintenanceTicket, Visitor
from django import forms

from django.utils import timezone
from datetime import timedelta

def dashboard(request):
    today = timezone.now()
    first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    # Financials
    total_rent_collected = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    net_income = total_rent_collected - total_expenses

    # Monthly Trends
    curr_month_revenue = Payment.objects.filter(date__gte=first_day_current_month).aggregate(Sum('amount'))['amount__sum'] or 0
    prev_month_revenue = Payment.objects.filter(date__gte=first_day_prev_month, date__lt=first_day_current_month).aggregate(Sum('amount'))['amount__sum'] or 0
    
    curr_month_expenses = Expense.objects.filter(date__gte=first_day_current_month.date()).aggregate(Sum('amount'))['amount__sum'] or 0
    prev_month_expenses = Expense.objects.filter(date__gte=first_day_prev_month.date(), date__lt=first_day_current_month.date()).aggregate(Sum('amount'))['amount__sum'] or 0
    
    curr_net_profit = curr_month_revenue - curr_month_expenses
    prev_net_profit = prev_month_revenue - prev_month_expenses
    
    profit_trend = 0
    if prev_net_profit > 0:
        profit_trend = ((curr_net_profit - prev_net_profit) / prev_net_profit) * 100
    elif curr_net_profit > 0:
        profit_trend = 100

    # Outstanding Rent (Current Month)
    active_leases = Lease.objects.filter(status='active')
    total_expected_rent = active_leases.aggregate(Sum('monthly_rent'))['monthly_rent__sum'] or 0
    outstanding_rent = max(0, total_expected_rent - curr_month_revenue)

    # Property Stats
    total_properties = Property.objects.count()
    total_units = Unit.objects.count()
    occupied_units = Unit.objects.filter(status='occupied').count()
    occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
    vacant_units_count = total_units - occupied_units

    # Action Alerts
    expiring_leases_count = Lease.objects.filter(
        status='active', 
        end_date__lte=today.date() + timedelta(days=30)
    ).count()
    
    # Simple overdue logic: active leases with no payment this month
    overdue_tenants_count = active_leases.exclude(
        tenant__payments__date__gte=first_day_current_month
    ).distinct().count()

    # Maintenance & Support
    recent_tickets = MaintenanceTicket.objects.order_by('-created_at')[:5]
    urgent_tickets_count = MaintenanceTicket.objects.filter(priority='emergency', status='open').count()

    # Visitors
    visitors_today = Visitor.objects.filter(entry_time__date=today.date()).count()
    currently_checked_in = Visitor.objects.filter(exit_time__isnull=True).count()

    context = {
        'total_rent_collected': total_rent_collected,
        'total_expenses': total_expenses,
        'net_income': net_income,
        'curr_month_revenue': curr_month_revenue,
        'curr_month_expenses': curr_month_expenses,
        'curr_net_profit': curr_net_profit,
        'profit_trend': round(profit_trend, 1),
        'outstanding_rent': outstanding_rent,
        'total_properties': total_properties,
        'total_units': total_units,
        'occupied_units': occupied_units,
        'occupancy_rate': round(occupancy_rate, 1),
        'vacant_units_count': vacant_units_count,
        'recent_tickets': recent_tickets,
        'urgent_tickets_count': urgent_tickets_count,
        'expiring_leases_count': expiring_leases_count,
        'overdue_tenants_count': overdue_tenants_count,
        'visitors_today': visitors_today,
        'currently_checked_in': currently_checked_in,
    }
    return render(request, 'pms/dashboard.html', context)

# Property Views
def property_list(request):
    properties = Property.objects.all()
    return render(request, 'pms/property_list.html', {'properties': properties})

def property_detail(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    units = property_obj.units.all()
    return render(request, 'pms/property_detail.html', {
        'property': property_obj,
        'units': units
    })

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'address', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'address': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }

def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user if request.user.is_authenticated else None # Handle case if user is not logged in for now
            property_obj.save()
            return redirect('property_detail', pk=property_obj.pk)
    else:
        form = PropertyForm()
    return render(request, 'pms/property_form.html', {'form': form, 'title': 'Add Property'})

# Unit Views
class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_number', 'unit_type', 'rent_amount', 'deposit_amount', 'status', 'water_meter', 'electricity_meter']
        widgets = {
            'unit_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'unit_type': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'water_meter': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'electricity_meter': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }

def unit_create(request, property_pk):
    property_obj = get_object_or_404(Property, pk=property_pk)
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.property = property_obj
            unit.save()
            return redirect('property_detail', pk=property_obj.pk)
    else:
        form = UnitForm()
    return render(request, 'pms/unit_form.html', {'form': form, 'property': property_obj})

# Tenant Views
def tenant_list(request):
    tenants = Tenant.objects.all()
    return render(request, 'pms/tenant_list.html', {'tenants': tenants})

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['first_name', 'last_name', 'id_passport_number', 'phone', 'email', 'emergency_contact', 'status', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'id_passport_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'emergency_contact': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 2}),
        }

def tenant_create(request):
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            return redirect('tenant_list')
    else:
        form = TenantForm()
    return render(request, 'pms/tenant_form.html', {'form': form})

# Lease Views
class LeaseForm(forms.ModelForm):
    class Meta:
        model = Lease
        fields = ['tenant', 'unit', 'start_date', 'end_date', 'monthly_rent', 'deposit_amount', 'payment_frequency', 'status']
        widgets = {
            'tenant': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'unit': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'start_date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'type': 'date'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'payment_frequency': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'status': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
        }

def lease_create(request):
    if request.method == 'POST':
        form = LeaseForm(request.POST)
        if form.is_valid():
            lease = form.save()
            # Update unit status to occupied
            lease.unit.status = 'occupied'
            lease.unit.save()
            return redirect('property_list')
    else:
        # Pre-fill fields if coming from unit detail
        unit_pk = request.GET.get('unit')
        initial = {}
        if unit_pk:
            unit = get_object_or_404(Unit, pk=unit_pk)
            initial = {
                'unit': unit,
                'monthly_rent': unit.rent_amount,
                'deposit_amount': unit.deposit_amount
            }
        form = LeaseForm(initial=initial)
    return render(request, 'pms/lease_form.html', {'form': form})

# Payment Views
def payment_list(request):
    payments = Payment.objects.all().order_by('-date')
    return render(request, 'pms/payment_list.html', {'payments': payments})

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['tenant', 'lease', 'amount', 'method', 'receipt_number', 'notes']
        widgets = {
            'tenant': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'lease': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'method': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'receipt_number': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'rows': 2}),
        }

def payment_create(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payment_list')
    else:
        tenant_pk = request.GET.get('tenant')
        initial = {}
        if tenant_pk:
            tenant = get_object_or_404(Tenant, pk=tenant_pk)
            initial = {'tenant': tenant}
            # Try to find an active lease
            active_lease = tenant.leases.filter(status='active').first()
            if active_lease:
                initial['lease'] = active_lease
                initial['amount'] = active_lease.monthly_rent
        form = PaymentForm(initial=initial)
    return render(request, 'pms/payment_form.html', {'form': form})
