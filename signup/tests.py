from datetime import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from signup.forms import SignUpForm
from signup.models import SignUpProfile

class TestSignup(TestCase):
    def test_signup(self):
        response = self.client.get(reverse("signup"))
        self.assertTemplateUsed(response, "signup/signup_form.html")

        response = self.client.post(reverse("signup"), {'email': 'foo@example.com'})
        self.assertEqual(SignUpProfile.objects.count(), 1)
        self.assertRedirects(response, reverse("signup_check_your_email"))

    def test_only_allow_one_email(self):
        User.objects.create_user('foo', 'foo@example.com', 'password')
        response = self.client.post(reverse("signup"), {'email': 'foo@example.com'})
        self.assertFormError(response, "form", "email", "Email address already in use.")
        self.assertTemplateUsed(response, "signup/signup_form.html")

    def test_send_activation_email(self):
        from signup.views import _send_activation_email
        from django.core import mail

        profile = SignUpProfile(email='foo@example.com')
        profile.save()
        _send_activation_email(profile)

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertTrue(profile.signup_key in msg.body)
        self.assertEqual(msg.to, [profile.email])

class TestActivate(TestCase):
    def setUp(self):
        self.profile = SignUpProfile(email='foo@example.com')
        self.profile.save()

    def test_activate_invalid_key(self):
        response = self.client.get(reverse("signup_activate", kwargs=dict(signup_key='zzz')))
        self.assertRedirects(response, reverse("signup_invalid_key"))

    def test_has_key_expired(self):
        profile = SignUpProfile(email='foo@example.com', expiry_date=datetime(1970, 1, 1))
        profile.save()
        self.assertTrue(profile.has_key_expired)

        profile = SignUpProfile(email='foo@example.com', expiry_date=datetime(2038, 1, 1))
        profile.save()
        self.assertFalse(profile.has_key_expired)

    def test_old_signup_key(self):
        profile = SignUpProfile(email='foo@example.com', expiry_date=datetime(1970, 1, 1))
        profile.save()
        count = SignUpProfile.objects.count()

        response = self.client.get(reverse("signup_activate", kwargs=dict(signup_key=profile.signup_key)))
        self.assertRedirects(response, reverse("signup_invalid_key"))
        self.assertEqual(SignUpProfile.objects.count(), count - 1)

    def test_activate_user(self):
        """
        Provide a valid signup key and create the user.
        """
        url = reverse("signup_activate", kwargs=dict(signup_key=self.profile.signup_key))
        response = self.client.post(url, dict(username='Foo', password='password'))

        self.assertRedirects(response, reverse("signup_success"))
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(email='foo@example.com')
        self.assertEqual(user.username, 'foo')

        self.assertEqual(SignUpProfile.objects.count(), 0)

    def test_user_clicks_activate_link(self):
        url = reverse("signup_activate", kwargs=dict(signup_key=self.profile.signup_key))
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'signup/activate_form.html')

    def test_activate_user_invalid_form(self):
        url = reverse("signup_activate", kwargs=dict(signup_key=self.profile.signup_key))
        response = self.client.post(url)
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "password", "This field is required.")

    def test_activate_with_existing_user(self):
        """
        Somebody has created a given username in the time between
        getting the signup_key and now activating it.
        """
        User.objects.create_user('foo2', 'foo2@example.com', 'password')
        url = reverse("signup_activate", kwargs=dict(signup_key=self.profile.signup_key))
        response = self.client.post(url, dict(username='foo2', password='password'))
        self.assertFormError(response, "form", "username", "Username already in use.")
