from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Technician, Appointment
from datetime import date

def appointment_calendar(request):
    today = date.today()
    
    # اولین روز ماه
    first_day = today.replace(day=1)
    # روز هفته اولین روز ماه (0=شنبه، 6=جمعه)
    first_day_weekday = first_day.weekday()  # Monday=0, Sunday=6
    # در تقویم فارسی: شنبه=0، جمعه=6
    # تبدیل به تقویم فارسی (برای نمایش درست)
    persian_weekday = (first_day_weekday + 2) % 7
    
    appointments = Appointment.objects.filter(date__month=today.month)
    
    # ایجاد لیست اعداد ۱ تا ۳۰ برای روزهای ماه
    days_range = range(1, 31)
    # روزهای خالی قبل از شروع ماه
    empty_days = range(persian_weekday)
    
    context = {
        'current_date': today,
        'appointments': appointments,
        'days_range': days_range,
        'empty_days': empty_days,
    }
    return render(request, 'appointments/calendar.html', context)

@login_required
def book_appointment(request):
    services = Service.objects.all()
    technicians = Technician.objects.filter(is_active=True)
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        technician_id = request.POST.get('technician')
        appointment_date = request.POST.get('date')
        appointment_time = request.POST.get('time')
        
        try:
            service = Service.objects.get(id=service_id)
            technician = None
            if technician_id:
                technician = Technician.objects.get(id=technician_id)
            
            appointment = Appointment.objects.create(
                customer=request.user,
                service=service,
                technician=technician,
                date=appointment_date,
                time=appointment_time,
                status='pending'
            )
            
            messages.success(request, 'نوبت شما با موفقیت ثبت شد!')
            return redirect('appointments:confirmation', appointment_id=appointment.id)
            
        except Exception as e:
            messages.error(request, f'خطا در ثبت نوبت: {str(e)}')
    
    context = {
        'services': services,
        'technicians': technicians,
    }
    return render(request, 'appointments/book.html', context)

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(customer=request.user).order_by('-date')
    return render(request, 'appointments/my_appointments.html', {'appointments': appointments})

@login_required
def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user)
    return render(request, 'appointments/confirmation.html', {'appointment': appointment})