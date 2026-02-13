from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_welcome_email(user):
    """ارسال ایمیل خوش‌آمدگویی بعد از ثبت‌نام"""
    subject = 'خوش آمدید به فروشگاه آنلاین ما!'
    
    html_message = render_to_string('shop/emails/welcome.html', {
        'user': user,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )

def send_order_confirmation_email(order):
    """ارسال ایمیل تأیید سفارش"""
    subject = f'تأیید سفارش #{order.id}'
    
    html_message = render_to_string('shop/emails/order_confirmation_email.html', {
        'order': order,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message,
        fail_silently=True,
    )

def send_appointment_confirmation_email(appointment):
    """ارسال ایمیل تأیید نوبت"""
    subject = f'تأیید نوبت #{appointment.id}'
    
    html_message = render_to_string('appointments/emails/appointment_confirmation.html', {
        'appointment': appointment,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.customer.email],
        html_message=html_message,
        fail_silently=True,
    )