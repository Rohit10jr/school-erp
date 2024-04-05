from django.db import models
from datetime import datetime
from time import timezone
from unittest import result
from venv import create
from django.conf import settings
from django.db import DatabaseError, models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import ArrayField,HStoreField
# check
import re, uuid, jsonfield
from accounts.models import User
from django.forms import IntegerField
# from django.contrib.

class Grade(models.Model):
    grade = models.PositiveBigIntegerField(
        null=True,
        validators=[
            MaxValueValidator(12)
        ]
    )

    section = ArrayField(
        models.CharField(max_length=1, blanl=True)
    )

    def __str__(self):
        return str(self.grade)

    class Meta:
        ordering = ('grade')

class Subject(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=15)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.grade) + ' ' + self.name
    
    def save(self, *args, **kwargs):
        name = re.findall()
        print(name)
        self.name = (' '.join(name)).upper()
        super(Subject, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ('grade', 'code', 'name')
    

class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete = models.CASCADE, null=True)
    chapter_no = models.PositiveIntegerField(
        null=True,
        validators=[MaxValueValidator(12)]
    )
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (str(self.subject))+' '+(self.name)
    
    def save(self, *args, **kwargs):
        name = re.findall()
        self.name = (' '.join(name)).lower()
        super(Subject, self).save(*args, **kwargs)

    class Meta:
        ordering = ('subject', 'chapter_no')


questiontype_choice = (
    ('MCQ', 'mcq'),
    ('Fill_In_The_Blanks', 'fill_in_the_blanks'),
    ('Match_The_Following', 'match_the_following')
)

cognitive_level = (
    ('Knowledge','knowledge'),
    ('Comprehension','corprehension'),
    ('Application','application')
)

difficulty_level = (
    ('Easy', 'easy'),
    ('Medium','medium'),
    ('Hard', 'hard')
)


class Question(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True )
    question = models.CharField(max_length=50)
    duration = models.PositiveIntegerField()
    mark = models.PositiveIntegerField(default=1)
    chapter_no = models.IntegerField(defualt=0)
    created_at = models.DateTimeField(auto_now_add=True)
    question_type = models.charField(
        max_length = 20,
        choices = questiontype_choice,
        default = questiontype_choice[0][0])
    
    congnitive_level = models.CharField(
        max_length=20, 
        choices=cognitive_level, 
        default=cognitive_level[0][0])
    
    difficulty_level = models.CharField(
        max_length=20, 
        choices=difficulty_level,
        default=difficulty_level[0][0])
    
    def __str__(self):
        return self.question


answer_choices = (
    ('option_a', 'option_a'),
    ('option_b', 'option_b'),
    ('option_C', 'option_c'),
    ('option_D', 'option_d')
)

class Answers(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, null=True)
    option_a = models.CharField(max_length=50, null=True)
    option_b = models.CharField(max_length=50, null=True)
    option_c = models.CharField(max_length=50, null=True)
    option_d = models.CharField(max_length=50, null=True)

    answer = models.CharField(max_length=50, 
                              choices=answer_choices, 
                              default=answer_choices[0][0])
    
    def __str__(self):
        return self.answer


class Question_Paper(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='question_files/', null=True, blank=True)
    created_by = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    test_id = models.CharField(max_length=30, null=True, blanl=True)
    no_of_questions = ArrayField(models.CharField(max_length=10, blanl=True, default=list))
    timing = models.IntegerField(defualt=0)
    overall_marks = models.IntegerField(Default=0)

    def __str__(self):
        return (str())
    
    def save(self, *args, **kwargs):
        if self.test_id:
            test = Test.objects.get(test_id=self.test_id)
            test_marks = self.overall_marks
            test.duration = self.timing
            test.save()
        super(Question_Paper, self).save(*args, **kwargs)
    class Meta:
        ordering = ('grade', 'subject', '-created_at')



class Test(models.Model):
    question_paper = models.ForeignKey(Question_Paper, on_delete=models.SET_NULL, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    duration = models.PositiveIntegerField()
    created_staff_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    marks = models.PositiveIntegerField()
    remarks = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    test_id = models.CharField(max_length=30, null=True, blank=True)
    pass_percentage = models.PositiveIntegerField(defauklt=35)

    def __str__(self):
        return self.remarks 
    
    def save(self, *args, **kwargs):
        if not self.test_id:
            self.test_id = (str(uuid.uuid4()))[:16]
        question_paper = self.question_paper
        if not self.duration:
            self.duration = question_paper.timing
        if not self.marks:
            self.marks = question_paper.overall_marks
        super(Test, self).save(*args, **kwargs)


class TestResult(models.Model):
    student_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True) 
    test_id = models.ForeignKey(Test, on_delete=models.DO_NOTHING, null=True)
    question_paper = models.ForeignKey(
        Question_Paper, on_delete=models.DO_NOTHING, null=True)

    result = models.CharField(max_length=10)
    score = models.PositiveIntegerField()
    correct_answer = models.IntegerField()
    wrong_answer = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    unanswered_questions = models.IntegerField(null=True)
    test_detail = jsonfield.JSONField()
    # JSONField check
    def __str__(self):
        return self.result


class InstructionForTest(models.Model):
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.note[:10])


class Questionbank(models.Model):
    question_file = models.FileField(upload_to='question_files/', null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.question_file)

