from curses.ascii import isalpha
from dataclasses import field
from operator import sub
from pyexpat import model
from collections import OrderedDict
from rest_framework import serializers, pagination
from rest_framework.response import Response
import re
from .models import Grade, Question_Paper, Subject, Chapter, Answers, Question, Test, TestResult, InstructionForTest




class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

    def validate(self, data):
        if not self.instance:
            if Grade.objects.filter(grade=data['grade']).exists():
                raise serializers.ValidationError({'error':'grade already exists'})
        return data


class SubjectSerializer(serializers.ModelSerializer):
    grade_name = serializers.SerializerMethodField('get_grade_name')

    def get_grade_name(self, subject):
        grade = Grade.objects.get(id=(subject.grade.id))
        return grade.grade
    
    class Meta:
        model = Subject
        fields = ['id', 'grade', 'grade_name', 'name', 'code', 'created_at']

    def validate(self, data):
        name = data['name']
        name = re.findall(r"[^\W\d_]+|\d+", name)
        if data['code'][:3].isalpha():
            code = re.match(r"([a-z]+)([0-9]+)", data['code'], re.I)
            if code:
                items = code.groups()
                code = items[1]

        else:
            code = data['code']

        data['name'] = (' '.join(name).upper())
        data['code'] = (data['name'][:3] + code)
        queyset = Subject.objects.all()
        if self.instance:
            id = self.instance.id
            queryset = queyset.exclude(id=id)
        if queryset.filter(name=data['name'], grade=data['grade']).exists():
            raise serializers.ValidationError({'error':'subject name already exists'})
        if queryset.filter(code=code).exists():
            raise serializers.ValidationError(
                {'error':'subject code already exists'}
            )
        return data



class ChapterSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField('get_subject_name')

    def get_subject_name(Self, chapter):
        print(chapter.subject)
        return (chapter.subject.name)
    
    class Meta:
        model = Chapter
        fields = ['id', 'subject', 'subject_name', 'name', 'chapter_no', 'description', 'created_at']

    def validate(self, data):
        name = data['name']
        name = re.findall(r"[^\W\d_]+|\d+", name)
        data['name'] = (' '.join(name)).lower()
        queryset = Chapter.objects.all()
        if self.instance:
            id = self.instance.id
            queryset = queryset.exclude(id=id)

        if queryset.filter(name=data['name'], subject=data['subject']).exists():
            raise serializers.ValidationError({'error':'chapter name already exists'})
        if queryset.filter(subject=data['subject'], chapter_no=data['chapter_no']).exists():
            raise serializers.ValidationError({'error':'chapter no already exists'})
        return data



class ChapterViewSerializer(serializers.Serializer):
    grade = serializers.IntegerField()
    subject = serializers.CharField()

class Question_answer_serilizer(serializers.Serializer):
    grade = serializers.StringRelatedField(many=True, source='Grade')


class questionanswerserializer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Subject.objects.all()
    )
    grade = serializers.SlugRelatedField(
        slug_field='grade',
        queyset=Grade.objects.all()
    )
    chapter =serializers.SlugRelatedField(
        slug_field='name',
        queryset=Chapter.objects.all()
    )

    class Meta:
        model = Question
        fields = ['id', 'grade', 'subject', 'chapter']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['option_a', 'option_b', 'option_c', 'option_d', 'answer']
        # fields = ['id', 'grade', 'subject', 'chapter']



class QuestionAnswerSerializer(serializers.ModelSerializer):
    grade_name = serializers.SerializerMethodField('get_grade_name')
    subject_name = serializers.SerializerMethodField('get_sbuject_name')
    chapter_name = serializers.SerializerMethodField('get_chapter_name')

    def get_grade_name(self, question):
        return question.grade.grade 
    
    def get_subject_name(self, question):
        return question.subject.name
    
    def get_chapter_name(self, question):
        return question.chapter.name
    
    answers = AnswerSerializer()

    class Meta:
        model = Question
        fields = ['id', 'grade', 'grade_name', 'subject', 'subject_name', 'chapter', 'chapter_name', 'question',
                  'question_type', 'cognitive_level', 'difficulty_level', 'mark', 'duration', 'answers']
        
        def create(self, validated_data):
            answers_data = validated_data.pop('answers')
            question = Question.objects.create(**validated_data)
            Answers.objects.create(question=question, **answers_data)
            return question
        
        def update(self, instance, validated_data):
            answers_data = validated_data.pop('answers')
            answers = instance.answers
            instance.grade = validated_data.get('grade', instance.grade)
            instance.subject = validated_data.get('subject', instance.subject)
            instance.chapter = validated_data.get('chapter', instance.chapter)
            instance.question = validated_data.get('question', instance.question)
            instance.question_type = validated_data.get(
            'question_type', instance.question_type)
            instance.cognitive_level = validated_data.get(
                'cognitive_level', instance.cognitive_level)
            instance.difficulty_level = validated_data.get(
                'difficulty_level', instance.difficulty_level)
            instance.save()

            answers.answer = answers_data.get('answer', answers.answer)
            answers.option_a = answers_data.get('option_a', answers.option_a)
            answers.option_b = answers_data.get('option_b', answers.option_b)
            answers.option_c = answers_data.get('option_c', answers.option_c)
            answers.option_d = answers_data.get('option_d', answers.option_d)
            answers.save()
            return instance

class QuestionGetSerializer2(serializers.ModelSerializer):
    number_of_questions = serializers.IntegerField()
    from_chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all(), default=None)
    to_chapter = serializers.PrimaryKeyRelatedField(
        queryset=Chapter.objects.all(), default=None 
    )
    all_chapters = serializers.BooleanField(required=False)
    customize = serializers.JSONField(required=False)

    class Meta:
        model = Question_Paper
        fields = ['grade', 'subject', 'number_of_questions', 'from_chapter',
                  'to_chapter', 'all_chapters', 'timing', 'overall_marks', 'customize']


class QuestionGetSerializer(serializers.ModelSerializer):
    customize = serializers.JSONField(required=False)
    list_of_questions = serializers.ListField()

    class Meta:
        model = Question_Paper
        fields = ['grade', 'subject', 'timing',
                  'overall_marks', 'customize', 'list_of_questions']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionPaperSerializer(serializers.ModelSerializer):
    grade_name = serializers.SerializerMethodField('get_grade_name')
    subject_name = serializers.SerializerMethodField('get_subject_name')

    def get_grade_name(self, subject):
        grade = Grade.objects.get(id=(subject.grade.id))
        return grade.grade

    def get_suject_name(self, chapter):
        subject = Subject.objects.get(id=(chapter.subject.id))
        return subject.name
    
    class Meta:
        model = Question_Paper
        fields = ['id', 'grade', 'grade_name', 'subject', 'subject_name', 'file',
                  'no_of_questions', 'test_id', 'overall_marks', 'timing', 'created_by', 'created_at']
        read_only_fields = ('test_id',)


class TestSerializer(serializers.ModelSerializer):
    grade_name = serializers.SerializerMethodField('get_grade_name')
    subject_name = serializers.SerializerMethodField('get_subject_name')

    def get_grade_name(self, subject):
        print(subject)
        grade = Grade.objects.get(id=(subject.grade.id))
        return grade.grade
    
    def get_subject_name(self, chapter):
        subject = Subject.objects.get(id=(chapter.subject.id))
        return subject.name
    
    class Meta:
        model = Test
        fields = ['id', 'grade', 'grade_name', 'subject', 'subject_name', 'question_paper',
                  'created_staff_id', 'duration', 'marks', 'pass_percentage', 'remarks', 'description', 'test_id']
        read_only_fields = ('test_id',)



class TestResultSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField('get_subject_name')
    register_number = serializers.SerializerMethodField
    ('get_register_no')

    def get_subject_name(self, test):
        print(test.subject.name)
        return test.subject.name
    
    def get_register_no(self, test):
        print(test.student_id.register_number, 'have commit')
        return test.student_id.register_number
    
    class Meta:
        model = TestResult
        fields = ['id', 'grade', 'subject', 'subject_name', 'register_number', 'student_id', 'test_id', 'question_paper', 'result', 'score', 'correct_answer', 'created_at', 'unansered_questions', 'wrong_answer', 'test_detail']



class TestInstruction(serializers.ModelSerializer):
    class Meta:
        model = InstructionForTest
        fields = '__all__'