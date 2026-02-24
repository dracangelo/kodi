from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Property(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    name = models.CharField(max_length=255)
    address = models.TextField()
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Unit(models.Model):
    UNIT_TYPES = (
        ('1BR', '1 Bedroom'),
        ('2BR', '2 Bedroom'),
        ('studio', 'Studio'),
        ('commercial', 'Commercial'),
    )
    STATUS_CHOICES = (
        ('occupied', 'Occupied'),
        ('vacant', 'Vacant'),
        ('maintenance', 'Under Maintenance'),
    )
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(max_length=50)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='vacant')
    water_meter = models.CharField(max_length=100, blank=True)
    electricity_meter = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.property.name} - {self.unit_number}"

class Tenant(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('past', 'Past'),
        ('blacklisted', 'Blacklisted'),
    )
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_passport_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    emergency_contact = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    rent_due_date = models.DateField(null=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['rent_due_date']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Lease(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expiring', 'Expiring'),
        ('terminated', 'Terminated'),
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='leases')
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_frequency = models.CharField(max_length=50, default='Monthly')
    lease_agreement = models.FileField(upload_to='leases/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        indexes = [
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"Lease: {self.tenant} at {self.unit}"

class Payment(models.Model):
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
    )
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('overdue', 'Overdue'),
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    lease = models.ForeignKey(Lease, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    receipt_number = models.CharField(max_length=100, unique=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Payment {self.receipt_number} - {self.amount}"

class Expense(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=100) # e.g. Repairs, Security
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    receipt_upload = models.FileField(upload_to='expenses/', blank=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"

class MaintenanceTicket(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    )
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_technician = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.id}: {self.category} at {self.unit.unit_number}"

class Visitor(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    id_number = models.CharField(max_length=50, blank=True)
    unit_visiting = models.ForeignKey(Unit, on_delete=models.CASCADE)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    security_guard_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Visitor: {self.name} to {self.unit_visiting}"
