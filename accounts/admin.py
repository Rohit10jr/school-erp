from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.http import HttpRequest
from rest_framework.authtoken.models import Token
from accounts.models import User, Profile 
from rest_framework.authtoken.models import TokenProxy as DRFToken
from django.shortcuts import redirect, render
from django.contrib.admin.sites import AdminSite
from .froms import CustomAuthenticationForm, Signup_form

# Register your models here.

class UserAdmin(UserAdmin):
    form = Signup_form
    add_form = Signup_form
    def has_module_permission(self, request):
        if request.user.is_anonymous:
            return True
        elif request.user.user_type == 'is_staff':
            return False
        elif request.user.user_type == 'is_amdin':
            return True
        
    list_display = ('register_number', 'email', 'phone', 'user_type')
    filter_horizontal = ()
    ordering_fields = ('register_number')
    serach_filters = ['register_number']
    list_filter = ('user_type', 'email')
    fieldsets = (
        (None, {'fields':('email', 'phone', 'register_number')}),
        ('permissoins', {'fields':('user_type')}),
        )
    add_fieldsets = (
        (None, {
            'classes':('wide'),
            'fields':('register_number', 'email', 'phone', 'user_type')
        })
        )

class ProfileAdmin(admin.ModelAdmin):
    def has_module_permission(self, request, obj=None):
        if request.user.is_anonymous:
            return True
        elif request.user.user_type == 'is_staff':
            return False
        elif request.user.user_type == 'is_amdin':
            return True
        

class TokenAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_anonymous:
            return True
        elif request.user.suer_type == 'is_staff':
            return False
        elif request.user.user_type == 'is_admin':
            return True


class GroupAdmin(admin.ModelAdmin):
    def has_module_permission(self, request, onj=None):
        if request.user.is_anonymous:
            return True
        elif request.user.user_type == 'is_staff':
            return False
        elif request.user.user_type == 'is_admin':
            return True
        

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.site_header = "School Adminstration"
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(DRFToken)
admin.site.register(DRFToken, TokenAdmin)
AdminSite.login_form = CustomAuthenticationForm