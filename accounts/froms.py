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
    email = forms.EmailField(widget=forms.TextInput(attrs ={"class":"form-control", "placeholder": "Email"} ))
    register_number = forms.CharField(wiget=forms.TextInput(attrs={"class": "form-control", "placeholder": "register Number"}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"class":"form-control", "placeholder":"date of birth"}))
    user_type = forms.ChoiceField(choices=usertype_choice)
    phone = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"phone"}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Frist name"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholdr":"Last name"}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Full name"}))
    address = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Address"}))
    standard = forms.CharField(widget=forms.TextInput(attrs={'classs':'form-control', 'placeholder':"Standard"}))
    section = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Section'}))
    data_entry_user = forms.BooleanField(required=False)



class login_form(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(
    attrs={"class": "form-control", "placeholder": "Email", "autocomplete": "off"}))
    phone = forms.CharField(widget=forms.TextInput(
    attrs={"class": "form-control", "placeholder": "Phone", "autocomplete": "off"}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['phone'].required = True


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label=("Email"),widget=forms.EmailInput(
        attrs={'autofocus': True}))
    password = forms.IntegerField(
    label=("Phone"),
    widget=forms.NumberInput(attrs={'autocomplete': 'current-password'}),
    )
    error_messages = {
        'invalid_login': (
            "Please enter a correct %(username)s and phone number. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': ("This account is inactive."),
    }

    def confirm_login_allowed(self, user):
        if user.user_type == 'is_student' or user.user_type == None:
            raise ValidationError(
        (" this account is inactive "), code = 'inactive',)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        phone = self.cleaned_data.get('password')

        if username is not None and phone:
            user = PasswordlessAuthBackend.authenticate(self.request,email=username,phone=phone)
            self.user_cache = PasswordlessAuthBackend.authenticate(self.request,email=username,phone=phone)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache) 

        return redirect('/admin')

    def get_user(self):
        return self.user_cache
    
    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages['invalid_login'],
            code = 'invalid_login',
            params = {'username':self.usernmae_field.verbose_name},
 
        )