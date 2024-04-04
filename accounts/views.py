from .permission import IsAdminUser, IsStaffUser
from .serializers import (
    SigninSerializer,
    SignupSerializer,
    ProfileSerializer,
    UserDetailsSerializer,
    OtpVerificationserializer
)
from django.contrib.auth import get_user_model
from http import client
from random import randint
from .auth_backend import PasswordlessAuthBackend
from django.db.models import Q
import profile
from django.shortcuts import render
from rest_framework.response import Response
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import (
    HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_203_NON_AUTHORITATIVE_INFORMATION, HTTP_206_PARTIAL_CONTENT
)
from utils.response import ResponseChoices
# check 
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from yaml import serialize
from .models import User, Profile, OTP
# Create your views here.
from utils.pagination import Pagination
User = get_user_model()


class SignupView(APIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    
    def post (self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status":ResponseChoices.SUCCESS, "message":f"user{serializer.validated_data.pop('first_name')} Registered Successfully"}, status=HTTP_201_CREATED)
        return Response({'status':ResponseChoices.FAILURE, "data":serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
# check these ResponseChoices


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if self.request.user:
            logout(request)
            return Response({'status':ResponseChoices.LOGOUT},
                            status=HTTP_200_OK)
        return Response({'status':'user doesnt logged in'}, status=HTTP_204_NO_CONTENT)


class SimpleLoginView(APIView):
    serializer_class = SigninSerializer
    permission_classes = [AllowAny]

    def post(Self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        if email and phone:
            try:
                # athuenticate
                user  = PasswordlessAuthBackend.authenticate(request, email=email, phone=phone)
                login(request, user)
                print(user)
            except Exception as e:
                # exception
                return Response({'status':str(e)})
            if user:
                # send data 
                token, creatd = Token.objects.get_or_create(user=user)
                data = {
                    'id': user.id,
                    'token': token.key,
                    'email': user.email,
                    'phone': user.phone,
                    'user_type': user.user_type,
                    'data_entry': user.is_data_entry,
                    'register_number': user.register_number
                }
            return Response({'status':ResponseChoices.SUCCESS,"data":data}, status=HTTP_200_OK)
        return Response({'status':'failed'}, status=HTTP_203_NON_AUTHORITATIVE_INFORMATION)


class LoginView(APIView):
    serializer_class = SigninSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        email  = request.data.get('email')
        phone = request.data.get('phone')

        if email and phone:
            try:
                user = PasswordlessAuthBackend.authenticate(request, email=email, phone=phone)
            except:
                return Response({'status':'user onest exist'}, status=HTTP_204_NO_CONTENT)
            if user:
                otp = randint(1111, 9999)
                OTP.objects.create(email=email, phone=phone, otp=otp)
                conn = client.HTTPConnection("2factor.in")
                conn.request("GET", "https://2factor.in/API/R1/?module=SMS_OTP&apikey=77d6322c-e7b5-11ec-9c12-0200cd936042/&to=" +
                             phone+"&otpvalue="+str(otp)+"&templatename=Login")
                return Response({'status':'otp generated successfully'}, status=HTTP_200_OK)
            return Response({'status':'failed'}, status=HTTP_203_NON_AUTHORITATIVE_INFORMATION)
            

class LoginVerifyView(APIView):
    serializer_class = OtpVerificationserializer
    permission_classes = [AllowAny]

    def post(self, request):
        phone = self.request.query_params.get('phone', None)
        email = self.request.query_params.get('email', None)
        otp = request.data.get('otp', None)
        otp2 = OTP.objects.filter(phone=phone)
        cc = (otp2.last()).otp 
        if otp == str(cc):
            user = User.objects.get(phone=phone, email=email)
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserDetailsSerializer(user)
            # ResponseChoices.SUCCESS Not working 
            return Response({"status": ResponseChoices.SUCCESS, 'data': serializer.data, 'token': token}, status=HTTP_200_OK)
        return Response({"status": 'failed'}, status=HTTP_203_NON_AUTHORITATIVE_INFORMATION)

class StudentProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, pk):
        if self.request.user.user_type == 'is_student' and self.request.user.id == pk:
            queryset = get_object_or_404(Profile, user=pk)
        else:
            return Response({'status': ' failure','message':'you dont have a permissions'}, 
            status=HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        serializer = ProfileSerializer(queryset)
        return Response(serializer.data, status=HTTP_200_OK)
    
    def update(self, request, pk):
        try :
            profile = Profile.objects.get(user=pk)
            serializer = ProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
        except Exception as e:
            return Response({'status': 'failure', 'data': str(e)}, status = HTTP_204_NO_CONTENT)


class UserDetailsView(ListAPIView, Pagination):
    serializer_class = UserDetailsSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        standard = self.request.query_params.get('standard')
        user_type = self.request.query_params.get('user_type')
        user = self.request.user
        queryset = []
        if user.user_type != '':
            if user.user_type == 'is_student':
                queryset = User.objects.get(id=user.id)
            elif user.user_type == 'is_staff':
                staff_standard = user.profile.standard
                print(staff_standard)
                queryset = User.objects.all()
                queryset = User.objects.filter(
                    user_type = 'is_student',
                    profile__standard__overlap=staff_standard)
                print(queryset)
            elif user.user_type == 'is_admin':
                queryset = User.objects.all()
            if standard and user.user_type != 'is_student':
                queyset = queryset.filter(
                    profile__standard__overlap=[standard])
                if user_type:
                    queyset = queyset.filter(user_type=user_type)
                print(queryset)
            else:
                if user.is_data_entry:
                    queryset = User.objects.all()
                    print(len(queryset))
            return queryset
        
    def list(self, request):
        try:
            user = request.user
            queryset = self.get_queryset()
            results = self.paginate_queryset(queryset)
            if user.user_type == 'is_student':
                serializer = UserDetailsSerializer(results)
            else:
                serializer = UserDetailsSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'status':'failure', 'data':str(e)}, status=HTTP_204_NO_CONTENT)

            




class UserDetailsEditView(RetrieveUpdateAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def retrieve(self, request, pk):
        try:
            requestuser = self.request.user
            if requestuser.id == pk:
                user = User.objects.get(pk=pk)
            else:
                if request.user_type == 'is_admin':
                    user = User.objects.get(Q(user_type='is_Staff', pk=pk)|Q(user_type='is_student', pk=pk))
                elif requestuser.user_type == 'is_staff':
                    user = User.objects.get(user_type='is_student', pk=pk)
            serializer = UserDetailsSerializer(user)
            return Response(serializer.data, status=HTTP_200_OK)
        except:
            return Response({"status": "User doesnt exist or you dont have permission "}, status=HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    serializer_class = UserDetailsSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    def get(self, request):
        user = self.request.user
        serializer = UserDetailsSerializer(user)
        return Response({"status":Response.SUCCESS, "data":serializer}, status=HTTP_200_OK)

    def load_section(request):
        standard = request.GET.get('standard', None)
        data = []
        student_list = User.objects.filter(
            user_type='is_student', profile_standard=standard
        )
        for i in student_list:
            section = (i.profile.section).upper()
            if section not in data:
                data.append(section)
        print(data)
        return render(request, 'accounts/sectiondropdown.html', {'items':data})
        UserDetailsSerializer



class check_for_user(APIView):
    serializer_class  = UserDetailsSerializer
    permission_classes = [AllowAny]

    def get(self, reqeust):
        email = (self.request.query_params.get('email'))
        phone = self.request.query_params.get('phone')
        users = User.objects.all()
        for i in users:
            if phone and i.phone == phone:
                return Response(status=HTTP_206_PARTIAL_CONTENT)
            if email and i.email == email.lower():
                return Response(status=HTTP_206_PARTIAL_CONTENT)
        return Response(status=HTTP_200_OK)