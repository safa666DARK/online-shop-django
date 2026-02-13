from django.contrib import admin
from .models import Service, Technician, Appointment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration']
    search_fields = ['name']

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'is_active']
    list_filter = ['is_active']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'service', 'date', 'time', 'status']
    list_filter = ['status', 'date']
    search_fields = ['customer__username', 'service__name']