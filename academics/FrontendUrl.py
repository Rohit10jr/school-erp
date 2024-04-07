from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from rest_framework.response import Response
from rest_framework import pagination
from django.conf import settings
import os
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile


def render_to_pdf(template_src, folder_name, params:dict):
    template = get_template(template_src)
    folder_name = folder_name
    html = template.render(params)
    result = BytesIO()
    filename = uuid.uuid4()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8'), result))
    try:
        with open(str(settings.BASE_DIR)+f'/media/{folder_name}/{filename}.pdf', 'wb+') as output:
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), output)
    except Exception as e:
        print(e)

    if pdf.err:
        return '', False
    
    return filename, True

def render_to_pdf2(template_src, folder_name, question_paper, params: dict):
    # print(questionb)
    template = get_template(template_src)
    folder_name = folder_name
    html = template.render(params)
    result = BytesIO()
    filename = str(uuid.uuid4())
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    exists = False

    if not question_paper:
        grade = params['grade']
        subject = params['subject']
        register_number = params['register_number']

        for file in os.listdir((str(settings.BASE_DIR)+f'/media/{folder_name}/')):
            filename = (str(file))
            if register_number in filename:
                exists = True
        filename = f'grade-{grade}&&subject-{subject}{register_number}'
        try:
            if exists:
                os.rename((str(settings.BASE_DIR)+f'/media/{folder_name}/{file}'), (str(
                    settings.BASE_DIR)+f'/media/{folder_name}/{filename}.pdf'))
            with open(str(settings.BASE_DIR)+f'/media/{folder_name}/{filename}.pdf', 'wb+') as output:
                pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), output)
        except Exception as e:
            print(e)
        return filename, True

    if pdf.err:
        print('error')
        return '', False
    questionfile = SimpleUploadedFile(
        filename+'.pdf', result.getvalue(), content_type='application/pdf')
    print(questionfile)
    question_paper.file = questionfile
    question_paper.save()
    return question_paper, True



class Paginate(pagination.PageNumberPagination):
    page_Size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        print(data)
        return Response({
            'links':{
                'previous': self.get_previous_link(), 
                'next': self.get_next_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })