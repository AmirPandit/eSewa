from django.db import models
from apps.base.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
