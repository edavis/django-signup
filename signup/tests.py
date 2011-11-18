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
