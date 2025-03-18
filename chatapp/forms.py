from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class registerform(forms.Form):
    first_name=forms.CharField(max_length=200, required=True)
    last_name=forms.CharField(max_length=200, required=True)
    email=forms.EmailField(max_length=200, required=True)
    passwd=forms.CharField(widget=forms.PasswordInput, required=True)

class signform(forms.Form):
    email=forms.EmailField(max_length=200, required=True)
    password=forms.CharField(widget=forms.PasswordInput, required=True)