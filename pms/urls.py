from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.property_create, name='property_create'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:property_pk>/units/add/', views.unit_create, name='unit_create'),
    path('units/', views.unit_list, name='unit_list'),
    path('units/quick-add/', views.unit_quick_create, name='unit_quick_create'),
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/add/', views.tenant_create, name='tenant_create'),
    path('leases/', views.lease_list, name='lease_list'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_create, name='payment_create'),
    path('expenses/add/', views.expense_create, name='expense_create'),
    path('tickets/add/', views.ticket_create, name='ticket_create'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('visitors/', views.visitor_list, name='visitor_list'),
    path('visitors/add/', views.visitor_create, name='visitor_create'),
]
