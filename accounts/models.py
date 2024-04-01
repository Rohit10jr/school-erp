from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from datetime import datetime
from django.contrib.postgres.fields import ArrayField


class MyUserMAanger(BaseUserManager):
    def create_user(self, email, phone, date_of_birth, register_number, is_data_entry):
        if not email:
            raise ValueError('enter email id')
        if not phone:
            try:
                phone = int(phone)
            except:
                raise ValueError('mobile number only number')
            raise ValueError('user must have mobile number')
        user = self.model(email=self.normalize_email(email))
        user.phone = phone
        user.date_of_birth = date_of_birth
        user.register_number = register_number
        user.is_daat_entry = is_data_entry
        user.save(using=self._db)
        return user
    def create_superuser(self, email, phone, user_type, date_of_birth, password, register_number):
        user = self.create_user(email=email, phone=phone, 
                                user_type=user_type, 
                                date_of_birth=date_of_birth,
                                password=password,
                                register_number=register_number
                            )
        user.set_password(user.password)
        if user_type == 'is_admin':
            user.user_type = 'is_admin'
        user.save(using=self._db)
        return user
    
    def create_satffuser(self, email, phone, user_type, date_of_birth, register_number):
        user = self.create_user(email=email, phone=phone, 
                                user_type=user_type,
                                date_of_birth=date_of_birth,
                                register_number=register_number)
        if user_type == 'is_staff':
            user.user_type = 'is_staff'

            user.save(using=self._db)
            return user

usertype_choice = (
    ('is_student', 'is_student'),
    ('is_staff', 'is_staff'),
    ('is_admin', 'is_admin')
)


class User(AbstractBaseUser):
    register_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, 
                             default=1234567890,
                             max_length=10,
                             validators=[
                                 MinLengthValidator(10)
                             ])
    date_of_birth = models.DateField(
        default=timezone.now, blan=True, null=True
    )
    user_type = models.CharField(
        max_length=20,
        choices=usertype_choice,
        default=None,
        blank=None,
        null=None,
    )
    is_data_entry = models.BooleanField(default=False)
    created_at = models.DateField(default=timezone.now)
    objects = MyUserMAanger()

    USERNAME_FIELD = ''
    REQUIRED_FIELDS = ['']

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        return self.user_type == 'is_staff' or self.user_type == 'is_admin'
     
    @property
    def is_admin(self):
        return self.user_type == 'is_admin'
    
    class Meta:
        ordering = ('created')


class Profile(models.Model):
    def upload_desgin_to(self, filename):
        return f'user_profile/{self.user.id}/{filename}'
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    frist_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    full_name = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to=upload_desgin_to, blank=True, null=True, default='user_profile/profile.png')
    standard =ArrayField(models.CharField(max_length=10, blank=True),blank=True, default=list)
    address = models.CharField(max_length=45, blank=True, null=True)

    def __str__ (self):
        return str(self.user)



class OTP(models.Models):
    email = models.EmailField()
    phone = models.CharField(default=1234567890, 
                             max_length=10, 
                             validators=[MinLengthValidator(10)])
    otp = models.CharField(max_length=6)

