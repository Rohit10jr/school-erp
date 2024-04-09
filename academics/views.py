from django.shortcuts import render

from ast import List
from base64 import standard_b64encode
from operator import truediv
from os import stat
import json
from utils.pagination import Pagination
from itertools import chain
from pickle import TRUE
from re import sub

from django.db.models import Count
from rest_framework.generics import (CreateAPIView, 
                                    RetrieveUpdateDestroyAPIView, 
                                    ListCreateAPIView, 
                                    ListAPIView, 
                                    RetrieveDestroyAPIView)
from utils.response import ResponseChoices
from accounts.permission import IsAdminUser, IsStaffUser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_206_PARTIAL_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_203_NON_AUTHORITATIVE_INFORMATION, HTTP_204_NO_CONTENT, HTTP_422_UNPROCESSABLE_ENTITY
)
from .forms import *
from django.conf import settings
from django.core.mail import send_mail
import random 
from .serializers import (
    SubjectSerializer,
    ChapterSerializer,
    GradeSerializer,
    ChapterViewSerializer,
    QuestionAnswerSerializer,
    QuestionGetSerializer,
    QuestionSerializer,
    QuestionPaperSerializer,
    TestSerializer,
    TestResultSerializer,
    TestInstruction,
) 
from .models import Question, Subject, Grade, Chapter, Question_Paper, Answers, Questionbank
from accounts.models import User
from .utils import render_to_pdf, render_to_pdf2
from utils.pagination import Paginator




class TestEditView(RetrieveUpdateDestroyAPIView):
    serializer_class = TestSerializer
    permission_classes = [AllowAny]
    queryset = Test.objects.all().order_by('grade', 'subject')

    def retrieve(self, request, pk):
        try:
            queryset = Test.objects.get(pk=pk)
        except:
            return Response({'status':'failure', 'data':'Test doesnt exists'}, status=HTTP_206_PARTIAL_CONTENT)
        serializer = TestSerializer(queryset)
        return Response(serializer.data, status=HTTP_206_PARTIAL_CONTENT)
        


class TestResultCreateView(CreateAPIView):
    serializer_class = TestResultSerializer
    queryset = TestResult.objects.all()
    permission_classes = [AllowAny]

    def get(self, request, foramt=None):
        queryset = TestResult.objects.all()
        grade = (self.request.query_params.get('grade'))
        student = self.request.query_params.get('student_id')
        test_id = self.request.query_params.get('test_id')
        if grade:
            if student:
                try:
                    grade = Grade.objects.get(grade=grade)
                    queryset = TestResult.objects.filter(
                        grade=grade, student_id=student)
                except:
                    queryset = TestResult.objects.all()
            else:
                try:
                    grade = Grade.objects.get(grade=grade)
                    queryset = TestResult.objects.filter(grade=grade) 
                except:
                    return Response({"status": ResponseChoices.FAILURE, 'data': serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
        elif test_id:
            queryset = TestResult.Objects.filter(test_id=test_id)
        queryset = TestResult.objects.all()
        print(type(queryset))
        data = self.paginate_queryset(queryset)
        serializer = TestResultSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)
    
    def create(self, request):
        serializer = TestResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':ResponseChoices.SUCCESS, 'data':serializer.data}, status=HTTP_201_CREATED)
        return Response({'status':ResponseChoices.FAILURE, 'data':serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)



class TestResultEditView(RetrieveDestroyAPIView):
    serializer_class = TestResultSerializer
    permission_classes = [AllowAny]
    queryset = TestResult.objects.all()

    def retrieve(self, request, pk):
        try:
            queryset = TestResult.objects.get(pk=pk)
        except:
            return Response({'status': 'failure', 'data':'test result doesnt exists'}, status=HTTP_206_PARTIAL_CONTENT)
        serializer = TestResultSerializer(queryset)
        return Response(serializer.data, status=HTTP_200_OK)
        

class TestInstructionView(ListCreateAPIView):
    serializer_class = TestInstruction
    queryset = InstructionForTest.objects.all()
    permission_classes = [AllowAny]

    def list(self, reqeust):
        queryset = InstructionForTest.objects.all()
        data = self.paginate_queryset(queryset)
        serializer = TestInstruction(data, many=True)
        return self.get_paginated_response(serializer.data)
    
    def create(self, request):
        serializer = TestInstruction(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": Response.SUCCESS, 'data': serializer.data}, status=HTTP_201_CREATED)
        return Response({"status": Response.FAILURE, "data": serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)


class EditTestInstructionView(RetrieveDestroyAPIView):
    serializer_class = TestInstruction
    queryset = InstructionForTest.objects.all()
    permission_classes = [AllowAny]

    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)

    def retrieve(self, request, pk):
        try:
            queryset = InstructionForTest.objects.get(id=pk)
        except:
             return Response({'status': 'failure', "data": "Instruction doesn't exists"}, status=HTTP_206_PARTIAL_CONTENT)
        serializer = TestInstruction(queryset)
        return Response(serializer.data, status=HTTP_200_OK)



def load_subject_chapter(request):
    grade_id = request.GET.get('grade', None)
    subject_id = request.GET.get('subject', None)
    if grade_id:
        subject = Subject.objects.filter(grade=grade_id).order_by('name')
        return render(request, 'academics/dropdown_list_options.html', {'items': subject})
    chapter = Chapter.objects.filter(subject=subject_id)
    return render(request, 'academics/dropdown_list_options.html', {'items': chapter})




def load_grade(request):
    user = request.user
    print(user)
    if user.user_type == 'is_admin':
        grades = Grade.objects.all()
    elif user.user_type == 'is_staff':
        standard = user.profile.standard
        grades = Grade.objects.filter(grade=standard)
    else:
        return None
    return render(request, 'academics/dropdown_grade.html', {'items': grades})


def load_test(request):
    # grade_id = request.GET.get('grade', None)
    subject_id = request.GET.get('subject', None)
    if subject_id:
        test = Test.objects.filter(subject_id=subject_id)
    return render(request, 'academics/test_dropdown.html', {'items': test})


def load_chapter_no(request):
    subject_id = request.GET.get('subject', None)
    chapter = Chapter.objects.filter(subject = subject_id)
    return render(request, 'academics/dropdown_chapter_no.html', {'items': chapter})




