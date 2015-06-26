from mongoengine import *
from allauth.account import app_settings
from mongoengine.django.mongo_auth.models import get_user_document
from mongoengine.django.utils import datetime_now
from django.utils.translation import ugettext_lazy as _
USER_DOCUMENT = get_user_document()
from django.utils import timezone
from moe_auth.auth import managers
from django.utils.crypto import get_random_string
from allauth.account import signals
from allauth.utils import build_absolute_uri
from allauth.account.adapter import get_adapter
from django.core.urlresolvers import reverse
import string

def _simple_domain_name_validator(value):
    """
    Validates that the given value contains no whitespaces to prevent common
    typos.
    """
    if not value:
        return False
    checks = ((s in value) for s in string.whitespace)
    if any(checks):
        return False
    return True
        # raise ValidationError(
        #     _("The domain name cannot contain any spaces or tabs."),
        #     code='invalid',
        # )

class Site(Document):
    site_id = IntField()
    domain = StringField(verbose_name=_('domain name'), max_length=100,
        validation=_simple_domain_name_validator
    )
    name = StringField(verbose_name=_('display name'), max_length=50)
    meta = {'queryset_class': managers.SiteQuerySet}

    class Meta:
        verbose_name = _('site')
        verbose_name_plural = _('sites')
        ordering = ('domain',)

    def __str__(self):
        return self.domain

class EmailAddress(Document):

    user = ReferenceField(USER_DOCUMENT,
                             verbose_name=_('user'))
    email = EmailField(unique=app_settings.UNIQUE_EMAIL,
                              verbose_name=_('e-mail address'))
    verified = BooleanField(verbose_name=_('verified'), default=False)
    primary = BooleanField(verbose_name=_('primary'), default=False)

    # objects = managers.EmailAddressManager()
    meta = {'queryset_class': managers.EmailAddressQuerset}
    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        if not app_settings.UNIQUE_EMAIL:
            unique_together = [("user", "email")]

    def __str__(self):
        return "%s (%s)" % (self.email, self.user)

    def set_as_primary(self, conditional=False):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        moe.auth.utils.user_email(self.user, self.email)
        self.user.save()
        return True

    def send_confirmation(self, request, signup=False):
        confirmation = EmailConfirmation.create(self)
        confirmation.send(request, signup=signup)
        return confirmation

    def change(self, request, new_email, confirm=True):
        """
        Given a new email address, change self and re-confirm.
        """

        moe.auth.utils.user_email(self.user, new_email)
        self.user.save()
        self.email = new_email
        self.verified = False
        self.save()
        if confirm:
            self.send_confirmation(request)

EmailAddress.add_to_class('objects',managers.EmailAddressQuerset(EmailAddress,EmailAddress.objects._collection))

class EmailConfirmation(Document):

    email_address = ReferenceField(EmailAddress,
                                      verbose_name=_('e-mail address'))
    created = DateTimeField(verbose_name=_('created'),
                                   default=datetime_now)
    sent = DateTimeField(verbose_name=_('sent'))
    key = StringField(verbose_name=_('key'), max_length=64, unique=True)

    # objects = managers.EmailConfirmationManager()
    meta = {'queryset_class': managers.EmailConfirmationQueryset}
    class Meta:
        verbose_name = _("email confirmation")
        verbose_name_plural = _("email confirmations")

    def __str__(self):
        return "confirmation for %s" % self.email_address

    @classmethod
    def create(cls, email_address):
        key = get_random_string(64).lower()
        return cls.objects.create(email_address=email_address,
                                           key=key)

    def key_expired(self):
        expiration_date = self.sent \
            + datetime.timedelta(days=app_settings
                                 .EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= timezone.now()
    key_expired.boolean = True

    def confirm(self, request):
        if not self.key_expired() and not self.email_address.verified:
            email_address = self.email_address
            get_adapter().confirm_email(request, email_address)
            signals.email_confirmed.send(sender=self.__class__,
                                         request=request,
                                         email_address=email_address)
            return email_address

    def send(self, request, signup=False, **kwargs):
        current_site = kwargs["site"] if "site" in kwargs \
            else Site.objects.get_current()
        activate_url = reverse("account_confirm_email", kwargs={'key':self.key})
        activate_url = build_absolute_uri(request,
                                          activate_url,
                                          protocol=app_settings.DEFAULT_HTTP_PROTOCOL)
        ctx = {
            "user": self.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": self.key,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        get_adapter().send_mail(email_template,
                                self.email_address.email,
                                ctx)
        self.sent = timezone.now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__,
                                             confirmation=self)
EmailConfirmation.add_to_class('objects',managers.EmailAddressQuerset(EmailConfirmation,EmailConfirmation.objects._collection))