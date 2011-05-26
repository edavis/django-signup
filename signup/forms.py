"""
Forms for django-signup.
"""

from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from models import SignUpProfile

class SignUpForm(ModelForm):
    def clean_email(self):
        # Check email address is not already in use
        if User.objects.filter(email=self.cleaned_data['email']):
            raise forms.ValidationError(u'Email address already in use.')
        return self.cleaned_data['email']

    class Meta:
        model = SignUpProfile
        fields = ('email', )

class ActivateForm(forms.Form):
    username = forms.CharField(required=True, max_length=250)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean_username(self):
        # Check username is not already in use
        if User.objects.filter(username=self.cleaned_data['username'].lower()):
            raise forms.ValidationError(u'Username already in use.')
        # Make sure username is lower case
        return self.cleaned_data['username'].lower()

    class Meta:
        fields = ('username', 'password')
