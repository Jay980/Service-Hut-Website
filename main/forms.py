from django.forms import ModelForm

from django import forms
from datetime import datetime
from .models import *
from django.contrib.auth.forms import UserCreationForm,UserChangeForm ,PasswordChangeForm
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models

User=get_user_model()

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CompanySignUpForm(ModelForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    
    class Meta:
        model = User
        fields = ('name', 'email','password', 'confirm_password')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            print("hello")
            return email
        raise forms.ValidationError('This email address is already in use.')


    def save(self,commit=True):
        print("hello")
        user=super(CompanySignUpForm,self).save(commit=False)
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
        return user    

class StudentSignUpForm(ModelForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    last_name=models.CharField(max_length=50)
    first_name=models.CharField(max_length=100)
    
    class Meta:
          model = User
          fields=("first_name", "last_name", "email", "password", "confirm_password",)

    def clean_email(self):
            email = self.cleaned_data.get('email')
            try:
               User.objects.get(email=email)
            except User.DoesNotExist:
               return email
            raise forms.ValidationError('This email address is already in use.')


    def save(self,commit=True):
        user=super(StudentSignUpForm,self).save(commit=False)
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
        return user   


class Service_Post(ModelForm):
    class Meta:
          model = Service
          fields=("category","role","location","content","charges")
        
    def __init__(self,user,*args,**kwargs):
        super(Service_Post,self).__init__(*args,**kwargs)


class Apply_Service(ModelForm):
    class Meta:
          model = Application
          fields=("resume", "cover_letter","available")


class AcceptReject(ModelForm):
    class Meta:
        model = Application
        fields=("is_accept","is_reject")


class EditStudentProfileForm(UserChangeForm):
    class Meta:
        model = Student
        fields = (
            'phone_no',
        
            'city',
            
        )

class EditEmployerProfileForm(UserChangeForm):

    class Meta:
        model = Company
        fields=(
            'image',
            "phone_no",
            "head_office_location",
            )

class EditService(ModelForm):

    class Meta:
        model = Service
        fields=("category","role","location","content","charges")
