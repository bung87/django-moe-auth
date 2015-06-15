from mongoengine.django.mongo_auth.models import get_user_document
from allauth.account.adapter import DefaultAccountAdapter as BaseAccountAdapter
from allauth.account import app_settings
from moe.auth.documents import Site
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

class DefaultAccountAdapter(BaseAccountAdapter):
    def new_user(self, request):
        return get_user_document()()
    def save_user(self, request, user, form,commit=True):
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']
        user.set_password(form.cleaned_data['password2'])
        user.save()
    def format_email_subject(self, subject):
        prefix = app_settings.EMAIL_SUBJECT_PREFIX
        if prefix is None:
            site = Site.objects.get_current()
            prefix = "[{name}] ".format(name=site.name)
        return prefix + force_text(subject)
    def confirm_email(self, request, email_address):
        # Marks the email address as confirmed and saves to the db.
        pass
    def generate_unique_username(self, txts, regex=None):
        #Returns a unique username from the combination of strings present in txts iterable.
        #  A regex pattern can be passed to the method to make sure the generated username matches it.
        pass
    def get_login_redirect_url(self, request):
        pass
    def get_logout_redirect_url(self, request):
        pass
    def get_email_confirmation_redirect_url(self, request):
        pass

class DefaultSocialAccountAdapter(object):
    pass