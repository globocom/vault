from django.utils.functional import SimpleLazyObject


class AuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if type(request.user) is SimpleLazyObject and request.session.get('user'):
            request.user = request.session.get('user')
        response = self.get_response(request)
        return response
