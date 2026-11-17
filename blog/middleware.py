from django.utils import translation
class ArabicOnlyMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        with translation.override('ar'):
            request.LANGUAGE_CODE = 'ar'
            response = self.get_response(request)
        response.headers['Content-Language'] = 'ar'
        if 'django_language' in request.COOKIES:
            response.delete_cookie('django_language', path='/')
        return response
