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