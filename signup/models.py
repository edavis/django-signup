"""
Models for django-signup.
"""

from django.conf import settings
from django.db import models
import datetime
import random
import hashlib

def generate_expiry_date():
    """
    Generate an expiry date SIGNUP_EXPIRY_DAYS days from now.
    """
    return datetime.datetime.now() + datetime.timedelta(settings.SIGNUP_EXPIRY_DAYS)

def generate_signup_key():
    """
    Generate a SHA1 hashed signup key.
    """
    r = str(random.random())
    return hashlib.sha1(r).hexdigest()

class SignUpProfile(models.Model):
    email = models.EmailField()
    signup_key = models.CharField(max_length=40, default=generate_signup_key)
    expiry_date = models.DateTimeField(default=generate_expiry_date)

    def __unicode__(self):
        return self.email

    @property
    def has_key_expired(self):
        return datetime.datetime.now() > self.expiry_date
