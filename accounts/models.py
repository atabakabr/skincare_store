from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    SKIN_CHOICES = [
        ('dry', 'خشک'),
        ('oily', 'چرب'),
        ('combo', 'ترکیبی'),
        ('sensitive', 'حساس'),

    ]


    skin_type=models.CharField(max_length=20,choices=SKIN_CHOICES,null=True,blank=True)
    concerns=models.JSONField(null=True, blank=True)
    preferences=models.JSONField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
