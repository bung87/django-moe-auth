# from allauth.account.models import EmailAddressManager as BaseEmailAddressManager
from allauth.account.models import EmailConfirmationManager as BaseEmailConfirmationManager
from mongoengine.queryset import QuerySet
# from mongoengine.queryset import QuerySetManager
SITE_CACHE = {}

class SiteQuerySet(QuerySet):
    use_in_migrations = True

    def _get_site_by_id(self, site_id):
        if site_id not in SITE_CACHE:
            site = self.get(site_id=site_id)
            SITE_CACHE[site_id] = site
        return SITE_CACHE[site_id]

    def _get_site_by_request(self, request):
        host = request.get_host()
        if host not in SITE_CACHE:
            site = self.get(domain__iexact=host)
            SITE_CACHE[host] = site
        return SITE_CACHE[host]

    def get_current(self, request=None):
        """
        Returns the current Site based on the SITE_ID in the project's settings.
        If SITE_ID isn't defined, it returns the site with domain matching
        request.get_host(). The ``Site`` object is cached the first time it's
        retrieved from the database.
        """
        from django.conf import settings
        if getattr(settings, 'SITE_ID', ''):
            site_id = settings.SITE_ID
            return self._get_site_by_id(site_id)
        elif request:
            return self._get_site_by_request(request)


    def clear_cache(self):
        """Clears the ``Site`` object cache."""
        global SITE_CACHE
        SITE_CACHE = {}
class EmailAddressQuerset(QuerySet):

    def __init__(self, document,collection):
        super(EmailAddressQuerset,self).__init__(document,collection)
        self.model = document
    def add_email(self, request, user, email,
          confirm=False, signup=False):
        try:
            email_address = self.get(user=user, email__iexact=email)
        except self.model.DoesNotExist:
            email_address = self.create(user=user, email=email)
            if confirm:
                email_address.send_confirmation(request,
                                                signup=signup)
        return email_address

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None

    def get_users_for(self, email):
        # this is a list rather than a generator because we probably want to
        # do a len() on it right away
        return [address.user for address in self.filter(verified=True,
                                                        email__iexact=email)]

    def fill_cache_for_user(self, user, addresses):
        """
        In a multi-db setup, inserting records and re-reading them later
        on may result in not being able to find newly inserted
        records. Therefore, we maintain a cache for the user so that
        we can avoid database access when we need to re-read..
        """
        user._emailaddress_cache = addresses

    def get_for_user(self, user, email):
        cache_key = '_emailaddress_cache'
        addresses = getattr(user, cache_key, None)
        if addresses is None:
            return self.get(user=user,
                            email__iexact=email)
        else:
            for address in addresses:
                if address.email.lower() == email.lower():
                    return address
            raise self.model.DoesNotExist()

# class EmailAddressManager(QuerySetManager):
#     # default = EmailAddressQuerset
#     model = None
#     def __init__(self, Document,queryset):
#         super(EmailAddressManager,self).__init__(Document,queryset)
#         self.model = Document


class EmailConfirmationQueryset(QuerySet):

    def __init__(self, document,collection):
        super(EmailConfirmationQueryset,self).__init__(document,collection)
        self.model = document



class EmailConfirmationManager(BaseEmailConfirmationManager):

    def __init__(self, document,collection):
        super(EmailConfirmationManager,self).__init__(document,collection)
        self.model = document
    @property
    def db(self):
        raise NotImplementedError

    def get_empty_query_set(self):
        return self.model.objects.none()

    def get_query_set(self):
        return self.model.objects
    # def get_queryset(self):
    #     return self._queryset_class(self.model)
    def contribute_to_class(self, model, name):
        super(EmailConfirmationManager, self).contribute_to_class(model, name)
        self.model = self._document
