from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# rest_framework
from rest_framework.decorators import api_view
from rest_framework.response import Response
# rest_framework render
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework import status
class HomeView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home.html'

    def get(self, request):
        return Response(template_name=self.template_name)
    
# sign up view
class SignupView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            # automatically login the user
            authenticate(request, username=username, password=password)
            login(request, user)
            
            return Response({'status': 'success', 'message': 'User created'}, status=status.HTTP_201_CREATED)
        
    def get(self, request):
        return render(request, 'signup.html')

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(username, password)
        # Check if the user exists
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'status': 'success', 'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
    def get(self, request):
        return render(request, 'login.html')
    
        

def logout_view(request):
    logout(request)
    return redirect('/')
