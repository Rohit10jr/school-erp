from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from datetime import datetime
from django.contrib.postgres.fields import ArrayField


class OTP(models.Models):
    email = models.EmailField()
    phone = models.CharField(default=1234567890, 
                             max_length=10, 
                             validators=[MinLengthValidator(10)])
    otp = models.CharField(max_length=6)

