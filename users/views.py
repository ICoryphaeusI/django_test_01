from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import RegistrationForm
from django.views.generic import CreateView
from .models import User	
from django.urls import reverse_lazy


class UserLoginView(LoginView):
    template_name = 'users/login.html'

class UserCreateView(CreateView):
    model = User
    template_name = 'users/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:login')
