from django.shortcuts import redirect
from django.urls import reverse
class PreventLoginRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated and trying to access the login page
        if request.user.is_authenticated and request.path == reverse('login'):
            username=request.user.username
            print(' middleware User is already authenticated', username)
            return redirect('/')
        # Check if the user is not authenticated and trying to access the detection page
        # if not request.user.is_authenticated and request.path == reverse('detection'):
        #     print('middleware User is not authenticated')
        #     return redirect('/login/')
        response = self.get_response(request)
        return response