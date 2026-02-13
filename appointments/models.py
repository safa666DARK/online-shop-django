from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام سرویس")
    description = models.TextField(verbose_name="توضیحات")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت")
    duration = models.IntegerField(default=30, verbose_name="مدت زمان (دقیقه)")
    
    def __str__(self):
        return self.name

class Technician(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام تکنسین")
    specialty = models.CharField(max_length=100, verbose_name="تخصص")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    def __str__(self):
        return f"{self.name} - {self.specialty}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('confirmed', 'تأیید شده'),
        ('completed', 'انجام شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="مشتری", related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="سرویس")
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تکنسین")
    date = models.DateField(verbose_name="تاریخ")
    time = models.TimeField(verbose_name="ساعت")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.username} - {self.service.name} - {self.date}"