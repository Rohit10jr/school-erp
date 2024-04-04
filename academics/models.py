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




class TestResult(models.Model):
    student_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True) 

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

