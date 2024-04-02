from re import sub 
from rest_framework.authtoken.models import Token

class SimpleMiddleware:
    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        return response
        
        # Code to be executed for each request/response after
        # the view is called.

    def process_view(self, request, view_func, view_args, view_kwargs):
        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        print(header_token)
        if header_token is not None:
            try:
                token = sub('Token', '', request.META.get('HTTP_AUTHORIZATION', None))
                token_obj = Token.objects.get(key=token)
                request.user = token_obj.user
                print(token_obj)
            except Token.DoesNotExist:
                print('hi')
            print(request.user)

