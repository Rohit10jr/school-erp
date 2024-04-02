from email.headerregistry import Address
from email.policy import default 
from typing_extensions import Required
from rest_framework import serializers
from django.shortcuts import get_list_or_404
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import send_mail
# from academics.forms import question_form
from .models import Profile

User = get_user_model()


usertype_choice = (
    (None),
    ('is_student', 'is_student'),
    ('is_staff', 'is_staff'),
    ('is_Admin', 'is_admin'),
)


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    phone = serializers.CharField()
    register_number = serializers.CharField(max_length=15)
    date_of_birth = serializers.DateField()
    user_type = serializers.ChoiceField(
        choices = usertype_choice,
        allow_blank = True,
        default = None
    )
    first_name = serializers.CharField(max_length=15)
    last_name = serializers.CharField(max_length=15)
    full_name = serializers.CharField(max_length=30)
    address = serializers.CharField(max_length=45)
    profile_picture = serializers.ImageField(
        required=False, max_length=None, allow_empty_file=True, use_url=True, default='user_profile/profile.png')
    standard = serializers.ListField(
        child=serializers.CharField(default=None), default=None)
    # section = serializers.CharField(max_length=2,allow_blank=True, default=None)
    is_data_entry = serializers.BooleanField()

    def validate(self, data):
        queryset = User.objects.all()
        if self.instance:
            id = self.instance.id
            queryset = queryset.exclude(id=id)
        if queryset.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'error':'email already exists'
            })
        elif queryset.filter(phone=data['phone']).exists():
            raise serializers.ValidationError({
                'error':'phone already exists'
            })
        return data

class SigninSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'phone']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'full_name', 'profile_picture', 'standard', 'address']  


class UserDetailSerailizer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'register_number', 'date_of_birth', 'is_active', 'user_type', 'creatd_at', 'profile']
        read_only_fields = ['id', 'created_at', 'user_type', 'is_daat_entry']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.register_number = validated_data.get('register_number', instance.register_number)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.active = validated_data.get('is_active', instance.is_active)
        instance.save()

        profile.first_name = profile_data.get(
            'first_name' , profile.first_name
        )

        profile.last_name = profile_data.get(
            'last_name', profile.last_name
        )

        profile.full_name = profile_data.get(
            'full_name', profile.full_name
        )

        profile.standard = profile_data.get(
            'standard', profile.standard
        )

        profile.address = profile_data.get(
            'address', profile.address
        )


class OtpVerificationserializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)