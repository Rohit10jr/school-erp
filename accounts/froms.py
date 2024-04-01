from dataclasses import fiedls 
from pyexpat import model 
from urllib import request
from django import forms 
from django.contrib.auth.base_user import AbstractBaseUser
from django.forms import ModelForm
from . models import *
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .auth_backend import PasswordlessAuthBackend
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import login
from django.shortcuts import redirect

usertype_choice = (
    (None, '------'),
    ('is_student', 'is_student'),
    ('is_staff', 'is_staff'),
    ('is_admin', 'is_admin')
)

class PickyAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user: AbstractBaseUser):
        if not user.user_type == "is_staff":
            raise ValidationError(("this account is inactive"), code='inactive')

class ProfileForn(forms.ModelForm):
    class Meta:
        model = Profile
        fiedls = '__all__'

class Signup_form(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class signup_form(forms.form):
    email = forms.EmailField(())
    register_number = forms.CharField(())
    date_of_birth = forms.DateField(())
    user_type = forms.ChoiceField(())
    phone = forms.CharField(())
    first_name = forms.CharField(())
    last_name = forms.CharField(())
    full_name = forms.CharField(())
    address = forms.CharField(())
    standard = forms.CharField(widget=forms.TextInput(attrs={'classs':'form-control', ''}))
    section = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Section'}))
    data_entry_user = forms.BooleanField(required=False)



class login_form(forms.Form):
    email = forms.EmailField(widget=forms.TextInput())
    phone = forms.CharField(())
    attrs = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['phone'].required = True