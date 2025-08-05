from django.db import models
from accounts.models import CustomUser 
from products.models import Product

INTERACTION_CHOICES = [
    ('view', 'View'),
    ('like', 'Like'),
    ('wishlist', 'Wishlist'),
    ('cart', 'Cart'),
]

class browsing_history(models.Model):
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product_id=models.ForeignKey(Product,on_delete=models.CASCADE)
    timestamp=models.DateTimeField(auto_now_add=True)
    interaction_type=models.CharField(max_length=20,choices=INTERACTION_CHOICES,default='view')
    quantity=models.PositiveIntegerField(default=1)
 