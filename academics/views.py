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




# class 
class SubjectCreateView(ListCreateAPIView, Pagination):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all().order_by('grade', 'code')
    permission_classes = [AllowAny]

    def list(self, request):
        queryset = self.get_queryset()
        grade = self.request.query_params.get('grade')
        if grade is not None:
            try:
                pass
            except:
                pass
            



class SubjectEditView(RetrieveDestroyAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    queryset = Subject.objects.all().order_by('grade', 'code')

    def retrieve(self, reqeust, pk):
        try:
            queryset = Subject.objects.get(pk=pk)
        except:
            return Response({'status': 'failure', "data": "Subject doesn't exists"}, status=HTTP_206_PARTIAL_CONTENT)
        serializer = SubjectSerializer(queryset)
        return Response(serializer.data, status=HTTP_200_OK)
    
    def update(self, request, pk):
        subject = Subject.objects.get(pk=pk)
        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_200_OK)
        return Response({"status": ResponseChoices.FAILURE, "data": serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)


class ChapterCreateView(CreateAPIView, Pagination):

    serializer_class = ChapterSerializer
    queryset = Chapter.objects.all().order_by('subject', 'order_no')
    permission_classes = [AllowAny]

    def get(self, format=None):
        queryset = Chapter.objects.all().order_by('subject', 'chapter_no')
        data = self.paginate_queryset(queryset)
        serializer = ChapterSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)
    
    def create(self, request):
        serializer = ChapterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_201_CREATED)
        return Response({"status":  ResponseChoices.FAILURE, "data": serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)


class ChapterEditView(RetrieveDestroyAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [AllowAny]
    queryset = Chapter.objects.all().order_by('subject', 'chapter_no')

    def retrieve(self, request, pk):
        try:
            queryset = Chapter.objects.get(pk=pk)
        except:
            return Response({'status': ResponseChoices.FAILURE, "data": "Chapter doesn't exists"}, status=HTTP_206_PARTIAL_CONTENT)
        serializer = ChapterSerializer(queryset)
        return Response(serializer.data)
    
    def update(self, request, pk):
        subject = Chapter.objects.get(pk=pk)
        serializer = ChapterSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_200_OK)
        return Response({"status": ResponseChoices.FAILURE, "data": serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)


class ChapterListView(APIView):
    serializer_class = ChapterViewSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        grade = request.dara.get('grade')
        subject = (request.data.get('subject'))
        try:
            if subject:
                data = []
                grade = Grade.objects.get(grade=grade)
                subject = Subject.objects.get(name=subject, grade=grade.id)
                chapters = (Chapter.objects.filter(subject=subject)
                            ).order_by('subject', 'chapter_no')
                for object in chapters:
                    data.append({
                        "id": object.id,
                        "subject": subject.name,
                        "subject_id": subject.id,
                        "grade": subject.grade.grade,
                        "name": object.name,
                        "chapter_no": object.chapter_no,
                        "description": object.description,
                    })
            if len(data):
                return Response({"status": ResponseChoices.SUCCESS, 'data': data})

        except:
            return Response({"status": "Not found"}, status=HTTP_206_PARTIAL_CONTENT)
        return Response({"status": ResponseChoices.FAILURE}, status=HTTP_206_PARTIAL_CONTENT)



class SubjectListView(ListAPIView, Pagination):
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Subject.objects.all()
        grade = self.request.query_params.get('grade')
        if grade is not None:
            try:
                grades = Grade.objects.get(grade=grade)
                queryset = (queryset.filter(grade=grades.id).order_by('code'))
            except:
                return Response({'status': ResponseChoices.FAILURE}, status=HTTP_206_PARTIAL_CONTENT)
            return queryset
        
    def list(self, request):
        queryset = self.get_queryset()
        data = self.paginate_queryset(queryset)
        serializer = SubjectSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)


class QuestionEditView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionAnswerSerializer
    permission_classes = [AllowAny]
    queryset = Question.objects.all()

    def retrieve(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
            serializer = QuestionAnswerSerializer(question)
            return Response({"status": ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_200_OK)
        except:
            return Response({'status': ResponseChoices.FAILURE, "data": "Question doesn't exists"}, status=HTTP_206_PARTIAL_CONTENT)
        

class QuestionPaperList(ListAPIView, Pagination):
    serializer_class = QuestionPaperSerializer
    permission_classes = [AllowAny]
    queryset = Question_Paper.objects.all().order_by('grade', 'subject')

    def get(self, request):
        grade = (self.request.query_params.get('grade'))
        subject = (str(self.request.query_params.get('subject'))).upper()
        if grade:
            grade = Grade.objects.get(grade=grade)
            try:
                subject = Subject.objects.get(grade=grade.id, name=subject)
                questions = Question_Paper.objects.filter(grade=grade.id, subject=subject.id)
            except:
                questions = Question_Paper.objects.filter(grade=grade.id)

        else:
            questions = Question_Paper.objects.all()
        data = self.paginate_queryset(questions)
        serializer = QuestionPaperSerializer(data, many=True)

        return self.get_paginated_response(serializer.data)




class QuestionPaperView(RetrieveDestroyAPIView):
    serializer_class = QuestionPaperSerializer
    permission_classes = [AllowAny]
    queryset = Question_Paper.objects.all()

    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, *args, **kwargs)
    def retrieve(self, request, pk):
        try:
            question_paper = Question_Paper.objects.get(pk=pk)
            serializer = QuestionPaperSerializer(question_paper)
            type = (self.request.query_params.get('type'))
            if type != None and (type).lower() == 'file':
                answers_list = []
                questions = question_paper.no_of_questions
                for question in questions:
                    question_from_model = Question.objects.get(id=question)
                    answers = Answers.objects.get(question=question_from_model)
                    answer = answers.answer
                    if answers.question.question_type == 'Fill_in_the_blanks':
                        answer = getattr(answers, str(answer))
                    answers_list.append(answer)
                user = self.request.user
                context = {'answers': answers_list, 'grade': question_paper.grade.grade,
                           'subject': question_paper.subject.name, 'register_number': user.register_number}
                filename, status = render_to_pdf2(
                    'academics/answer_file.html', 'answer_files', None, context)
                if not status:
                    return Response({'status': 'given details incorrect'}, status=HTTP_200_OK)
                return Response({'path': f'/media/answer_files/{filename}.pdf', 'data': serializer.data}, status=HTTP_200_OK)
            return Response({'status': ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_200_OK)

        except:
            return Response({"status": ResponseChoices.FAILURE, "data": "Question-paper doesn't exists"}, status=HTTP_206_PARTIAL_CONTENT)



class QuestionFormQuestionPaper(APIView):
    serializer_class = QuestionAnswerSerializer
    queryset = Question.objects.all().order_by('grade', 'subject', 'chapter')
    permission_classes = [AllowAny] 

    def get(self, request, format=None):
        question_paper_id = (self.request.query_params.get('question_paper'))
        question_paper = Question_Paper.objects.get(id=question_paper_id)
        question_list = question_paper.no_of_questions
        data = []
        change = False
        for i in question_list:
            try:
                queryset = Question.objects.get(id=int(i))
                data.append((QuestionAnswerSerializer(queryset)).data)
            except:
                question_list.remove(i)
                change = True
        if change:
            question_paper.no_of_questions = question_list
            question_paper.save()
        return Response(data)


class TestCreateView(CreateAPIView):
    serializer_class = TestSerializer
    queryset = Test.objects.all().order_by('grade', 'subject')
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        grade = (self.request.query_params.get('grade'))
        test_id = (self.request.query_params.get('test_id'))
        if grade:
            queryset = Test.objects.filter(grade=grade)
            data = self.paginate_queryset(queryset)
            serializer = TestSerializer(data, many=True)

        if test_id:
            try:
                queryset = Test.objects.get(test_id=test_id)
                print(queryset)
                serializer = TestSerializer(queryset)
                print(serializer)
                return Response({'status': ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_200_OK)
            except:
                return Response({"status": "failure", "data": "please give a valid test id"}, status=HTTP_206_PARTIAL_CONTENT)
            
        else:
            queryset = Test.objects.all().objects_by('grade', 'subject')
            data = self.paginate_queryset(queryset)
            serializer = TestSerializer(data, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        serializer = TestSerializer(data=request.data)
        if serializer.is_valid():
            question_paper = request.data['question_paper']
            serializer.save()
            Test_obj = Test.objects.get(question_paper=question_paper)
            question_paper = Question_Paper.objects.get(id= question_paper)
            question_paper.test_id = Test_obj.test_id
            question_paper.save()
            return Response({"status": ResponseChoices.SUCCESS, 'data': serializer.data}, status=HTTP_201_CREATED)
        return Response({"status": ResponseChoices.FAILURE, "data": serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)


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
        
    def update(self, request, pk):
        test = Test.objects.get(pk=pk)
        serializer = TestSerializer(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':ResponseChoices.SUCCESS, 'data':serializer.data}, status=HTTP_200_OK)
        return Response({"status":ResponseChoices.FAILURE, 'data':serializer.errors}, status=HTTP_206_PARTIAL_CONTENT)
    
    def destroy(self, request, pk, *args, **kwargs):
        test = Test.objects.get(id=pk)
        test_id = test.test_id
        question_paper = Question.objedcts.get(test_id=test_id)
        question_paper.test_id = None
        question_paper.save()
        return super(TestEditView, self).destroy(request, *args, **kwargs)




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




