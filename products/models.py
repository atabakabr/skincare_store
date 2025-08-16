import uuid
from django.db import models
from accounts.models import CustomUser

class SkinType(models.Model):
    name=models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Concern(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name=models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Tag(models.Model):
    name=models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Product(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=200)
    brand=models.CharField(max_length=100)

    class Category(models.TextChoices):
        CLEANER='cleaner','Cleaner'
        SERUM='serum','Serum'
        MOISTURIZER='moisturizer','Moisturizer'
        

    category=models.CharField(max_length=20)
    skin_type=models.ManyToManyField(SkinType,blank=True)
    concerns_targeted=models.ManyToManyField(Concern,blank=True)
    ingredients=models.ManyToManyField(Ingredient,blank=True)
    tags=models.ManyToManyField(Tag,blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    rating=models.FloatField(default=0.0)
    rate_quantity=models.IntegerField(default=0)
    image_url=models.URLField(max_length=500,blank=True)
    image=models.ImageField(upload_to='products/',null=True,blank=True)
    quantity=models.PositiveIntegerField(default=0)
    sold_quantity=models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} by {self.brand}"



class UserRating(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    rating=models.PositiveSmallIntegerField()

    class Meta:
        unique_together=('user','product')


class Wishlist(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)

    class Meta:
        unique_together=('user','product')
