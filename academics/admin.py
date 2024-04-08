from django.contrib import admin
from django.http import HttpRequest
from .models import Grade, Subject, Chapter, Question,Question_Paper, Test, TestResult 
# Register your models here.

class SubjectAdmin(admin.ModelAdmin):
    def has_module_permission(self, request, obj=None):
        if request.user.is_anonymous:
            return True
        elif request.user.useR_type == 'is_staff':
            return False
        elif request.user.user_type == 'is_admin':
            return True
        
class GradeAdmin(admin.ModelAdin):
    def has_module_permission(self, request, obj=None):
        if request.user.is_anonymous:
            return True
        elif request.user.user_type == 'is_staff':
            return False
        elif request.user.user_type == 'is_admin':
            return True
        
admin.site.register(Grade, GradeAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Chapter)
admin.site.register(Question)
admin.site.register(Question_Paper)
admin.site.register(Test)
admin.site.register(TestResult)
