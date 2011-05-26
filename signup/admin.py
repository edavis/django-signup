"""
Admin models for django-signup.
"""

from django.contrib import admin
from models import SignUpProfile

class SignUpProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(SignUpProfile, SignUpProfileAdmin)
