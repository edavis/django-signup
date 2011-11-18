"""
Views for django-signup.
"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from models import SignUpProfile
from forms import SignUpForm, ActivateForm
import datetime

def _send_activation_email(profile):
    # Render activation email
    message = render_to_string('signup/activation_email.txt',
                                {'signup_key': profile.signup_key})
    subject = render_to_string('signup/activation_email_subject.txt')
    # Send activation email
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [profile.email,],
                fail_silently=True)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            instance = form.save()
            # Generate and send activation email
            _send_activation_email(instance)
            return HttpResponseRedirect(reverse("signup_check_your_email"))
    else:
        form = SignUpForm()
    return render(request, 'signup/signup_form.html', {'form': form})

def activate(request, signup_key):
    # Try and get a sign up profile that matches activation key
    # Redirect to failure page if no match
    try:
        profile = SignUpProfile.objects.get(signup_key=signup_key)
    except:
        return HttpResponseRedirect(reverse("signup_invalid_key"))
    # Check if profile has expired
    if not profile.has_key_expired:
        if request.method == 'POST':
            form = ActivateForm(request.POST)
            if form.is_valid():
                # Create a new User instance
                user = User(username=form.cleaned_data['username'],
                                email=profile.email)
                user.set_password(form.cleaned_data['password'])
                user.save()
                # Delete the sign up profile
                profile.delete()
                return HttpResponseRedirect(reverse("signup_success"))
        else:
            form = ActivateForm()
    else:
        # Delete expired sign up profile and show invalid key page
        profile.delete()
        return HttpResponseRedirect(reverse("signup_invalid_key"))
    return render(request, 'signup/activate_form.html', {'form': form})
