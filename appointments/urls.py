from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_calendar, name='calendar'),  # این خط مهمه
    path('book/', views.book_appointment, name='book'),
    path('my/', views.my_appointments, name='my'),
    path('confirmation/<int:appointment_id>/', views.appointment_confirmation, name='confirmation'),
]