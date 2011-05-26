"""
Models for django-signup.
"""

from django.conf import settings
from django.db import models
import datetime
import random
import hashlib

class SignUpProfile(models.Model):
    email = models.EmailField()
    signup_key = models.CharField(max_length=40)
    expiry_date = models.DateTimeField()

    class Meta:
        pass

    def __unicode__(self):
        return unicode(self.email)

    def save(self):
        # Generate activation key
        self.signup_key = hashlib.sha1(str(random.random())).hexdigest()
        # Set expiry date
        self.expiry_date = datetime.datetime.now() + \
                            datetime.timedelta(settings.SIGNUP_EXPIRY_DAYS)
        super(SignUpProfile, self).save()
