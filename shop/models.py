from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="دسته‌بندی")
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    description = models.TextField(verbose_name="توضیحات")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت")
    stock = models.IntegerField(default=0, verbose_name="موجودی")
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="تصویر")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def view_count(self):
        return 0  # می‌تونی بعداً پیاده‌سازی کنی

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="سبد خرید")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    quantity = models.IntegerField(default=1, verbose_name="تعداد")
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def total_price(self):
        return self.product.price * self.quantity
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال آماده‌سازی'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="سبد خرید")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ کل")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    shipping_address = models.TextField(verbose_name="آدرس ارسال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول", related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="امتیاز")
    comment = models.TextField(verbose_name="نظر")
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True, verbose_name="تأیید شده")  # اضافه شد
    
    class Meta:
        ordering = ['-created_at']  # جدیدترین نظرات اول
        unique_together = ['user', 'product']  # هر کاربر یک نظر
    
    def __str__(self):
        return f"نظر {self.user.username} برای {self.product.name}"
    
    def get_stars(self):
        """تولید HTML برای نمایش ستاره‌ها"""
        stars = '★' * self.rating + '☆' * (5 - self.rating)
        return f'<span style="color: #f39c12;">{stars}</span>'

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.name}"
    
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="سفارش")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="مبلغ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    authority = models.CharField(max_length=100, blank=True, verbose_name="کد Authority")
    ref_id = models.CharField(max_length=100, blank=True, verbose_name="کد پیگیری")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for Order #{self.order.id}"