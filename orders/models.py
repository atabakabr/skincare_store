from django.db import models
from accounts.models import CustomUser
from products.models import Product

class order(models.Model):
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    timestamp=models.DateTimeField(auto_now_add=True)
    is_paid=models.BooleanField(default=False)

class ord_items(models.Model):
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price_at_purchase=models.DecimalField(max_digits=10, decimal_places=2)
    ord=models.ForeignKey(order,on_delete=models.CASCADE)

class cart_item(models.Model):
    ord=models.ForeignKey(order,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=0)
    added_at=models.DateTimeField(auto_now_add=True)
