from django.db import models
import uuid
from accounts.models import CustomUser
from products.models import SkinType,Concern

class question(models.Model):
    text=models.TextField()


class quiz_results(models.Model):
    quiz_id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    skin_type=models.ForeignKey(SkinType,on_delete=models.CASCADE)
    concerns=models.ManyToManyField(Concern)
    preferences=models.JSONField(null=True, blank=True)
    timestamp=models.DateTimeField(auto_now_add=True)

