"""
URLconf for django-signup.
"""

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from signup import views

urlpatterns = patterns('',
    url(r'^$', views.signup, name="signup"),
    url(r'^checkyouremail/$',
            direct_to_template, {'template': 'signup/check_email.html'},
            name="signup_check_your_email"),
    (r'^activate/(?P<signup_key>[-\w]+)/$', views.activate),
    (r'^key_invalid/$',
            direct_to_template, {'template': 'signup/key_invalid.html'}),
    (r'^success/$',
            direct_to_template, {'template': 'signup/signup_successful.html'}),
)
