from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from .models import Album, Photo

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    class Meta:
        model = User
        fields = ['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class SimplePasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        return self.cleaned_data.get('new_password1')

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch')
        return password2

class UsernamePasswordResetForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=254)

    def get_users(self, username):
        active_users = User._default_manager.filter(username__iexact=username, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, request=None, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, html_email_template_name=None,
             extra_email_context=None):
        username = self.cleaned_data['username']
        for user in self.get_users(username):
            if not domain_override:
                domain = request.get_host() if request else ''
                site_name = domain
            else:
                domain = domain_override
                site_name = domain_override
            email = user.email or f"{user.username}@example.com"
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            subject = render_to_string(subject_template_name, context)
            subject = ''.join(subject.splitlines())
            body = render_to_string(email_template_name, context)
            email_message = EmailMultiAlternatives(subject, body, from_email, [email])
            if html_email_template_name:
                html_email = render_to_string(html_email_template_name, context)
                email_message.attach_alternative(html_email, 'text/html')
            email_message.send()

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image']


class SimpleSetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label='New password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )
    new_password2 = forms.CharField(
        label='Confirm new password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('The two password fields did not match.')
        return cleaned
