from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from datetime import datetime
from .models import Product, Category, Cart, CartItem, Order, ProductReview, Payment
from .utils import send_order_confirmation_email
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .utils import send_welcome_email
from appointments.models import Service


def home(request):
    products = Product.objects.all()[:8]
    categories = Category.objects.all()[:6]
    
    # اضافه کردن سرویس‌های نوبت‌دهی (خدمات آموزشی)
    services = Service.objects.all()[:6]  # حداکثر ۶ سرویس نمایش بده
    
    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories,
        'services': services,  # اضافه شد!
    })

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = cart.total_price() if hasattr(cart, 'total_price') else 0
    
    context = {
        'items': items,
        'total': total,
        'cart': cart,
    }
    return render(request, 'shop/cart_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('shop:cart_detail')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shop:cart_detail')

from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def home(request):
    products = Product.objects.all()[:8]
    categories = Category.objects.all()[:6]
    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories
    })

@login_required
def buy_now(request, product_id):
    """خرید سریع بدون رفتن به سبد خرید"""
    product = get_object_or_404(Product, id=product_id)
    
    # ایجاد سبد خرید موقت
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # پاک کردن موارد قبلی سبد خرید
    cart.items.all().delete()
    
    # اضافه کردن محصول به سبد
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    
    # هدایت به checkout
    return redirect('shop:checkout')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'shop/category_list.html', {'categories': categories})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    
    # گرفتن نظرات تأیید شده
    reviews = product.reviews.filter(approved=True).order_by('-created_at')
    
    # محاسبه میانگین امتیاز
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    
    # محصولات مرتبط
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', 'newest')
    in_stock = request.GET.get('in_stock', False)
    
    # شروع با همه محصولات
    products = Product.objects.all()
    
    # فیلتر بر اساس جستجو
    if query:
        products = products.filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query)
        )
    
    # فیلتر دسته‌بندی
    if category_id:
        products = products.filter(category_id=category_id)
    
    # فیلتر قیمت
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # فقط موجود
    if in_stock:
        products = products.filter(stock__gt=0)
    
    # مرتب‌سازی
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        # اینجا می‌تونی فیلد view_count اضافه کنی
        products = products.order_by('-view_count')
    
    # گرفتن همه دسته‌بندی‌ها برای فیلتر
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'query': query,
        'categories': categories,
        'selected_category': category_id,
        'selected_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
    }
    return render(request, 'shop/search_results.html', context)

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if cart.items.count() == 0:
        return redirect('shop:cart_detail')
    
    # محاسبه هزینه ارسال
    shipping_cost = 0 if cart.total_price() > 100000 else 15000
    final_price = cart.total_price() + shipping_cost
    
    if request.method == 'POST':
        # گرفتن اطلاعات
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        
        # ایجاد سفارش
        order = Order.objects.create(
            user=request.user,
            cart=cart,
            total_price=final_price,
            shipping_address=f"{first_name} {last_name}\n{address}\n{city} - کد پستی: {postal_code}",
            status='pending'
        )
        
        # هدایت به صفحه پرداخت
        return redirect('shop:process_payment', order_id=order.id)
    
    context = {
        'cart': cart,
        'shipping_cost': shipping_cost,
        'final_price': final_price,
    }
    return render(request, 'shop/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})

# توابع احراز هویت ساده
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('shop:home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
    return render(request, 'shop/login.html')

def logout_view(request):
    logout(request)
    return redirect('shop:home')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')  # ایمیل رو بگیر (اختیاری نیست)
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # اعتبارسنجی‌ها
        errors = []
        
        if not username:
            errors.append('نام کاربری الزامی است')
        if not email:
            errors.append('ایمیل الزامی است')
        elif User.objects.filter(email=email).exists():
            errors.append('این ایمیل قبلاً ثبت شده است')
        if not password1:
            errors.append('رمز عبور الزامی است')
        if password1 != password2:
            errors.append('رمز عبور و تکرار آن مطابقت ندارند')
        if User.objects.filter(username=username).exists():
            errors.append('این نام کاربری قبلاً ثبت شده است')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'shop/register.html')
        
        # ایجاد کاربر جدید **با ایمیل**
        user = User.objects.create_user(
            username=username,
            email=email,  # ایمیل هم اضافه شد
            password=password1
        )
        
        # ارسال ایمیل خوش‌آمدگویی
        try:
            send_welcome_email(user)
        except Exception as e:
            print(f"خطا در ارسال ایمیل خوش‌آمدگویی: {e}")
            # خطای ایمیل ثبت‌نام رو مختل نکنه
        
        login(request, user)
        messages.success(request, 'ثبت‌نام با موفقیت انجام شد! یک ایمیل خوش‌آمدگویی برایتان ارسال شد.')
        return redirect('shop:home')
    
    return render(request, 'shop/register.html')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})

def popular_products(request):
    products = Product.objects.order_by('-view_count')[:10]
    return render(request, 'shop/popular_products.html', {'products': products})

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        # اینجا می‌تونی مدل Review رو ایجاد کنی
        messages.success(request, 'نظر شما ثبت شد!')
        return redirect('shop:product_detail', id=product_id)
    return redirect('shop:product_detail', id=product_id)

@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('shop:cart_detail')

@login_required
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()  # اگر ۱ بود، حذف کن
    return redirect('shop:cart_detail')

@login_required
def process_payment(request, order_id):
    """پرداخت تستی - در واقعیت به زرین‌پال وصل میشه"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # ایجاد رکورد پرداخت
        payment = Payment.objects.create(
            order=order,
            amount=order.total_price,
            status='success',  # در تست موفق فرض می‌کنیم
            ref_id=f"TEST-{order.id}-{datetime.now().timestamp()}"
        )
        
        # آپدیت وضعیت سفارش
        order.status = 'paid'
        order.save()

        # ارسال ایمیل تأیید
        try:
            send_order_confirmation_email(order)
        except Exception as e:
            print(f"خطا در ارسال ایمیل: {e}")
            # خطای ایمیل نباید پرداخت رو مختل کنه
        
        # خالی کردن سبد خرید
        order.cart.items.all().delete()
        
        messages.success(request, f'پرداخت با موفقیت انجام شد! کد پیگیری: {payment.ref_id}')
        return redirect('shop:order_confirmation', order_id=order.id)
    
    context = {
        'order': order,
        'payment_amount': order.total_price,
    }
    return render(request, 'shop/payment.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # بررسی آیا کاربر قبلاً نظر داده
    existing_review = ProductReview.objects.filter(product=product, user=request.user).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if existing_review:
            # آپدیت نظر موجود
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, 'نظر شما ویرایش شد!')
        else:
            # ایجاد نظر جدید
            ProductReview.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'نظر شما با موفقیت ثبت شد!')
        
        return redirect('shop:product_detail', id=product_id)
    
    context = {
        'product': product,
        'existing_review': existing_review,
    }
    return render(request, 'shop/add_review.html', context)