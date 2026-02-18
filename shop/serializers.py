from rest_framework import serializers
from .models import Product  # اگه اسم مدل محصولت فرق داره، عوضش کن

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  # همه فیلدهای مدل رو برمی‌گردونه