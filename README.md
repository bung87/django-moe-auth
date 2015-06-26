# Django Moe Auth


## Requirements

* Python
* Django
* mongoengine==0.8.8
* djangorestframework==3.0.5
* django-allauth>=0.19.1

## Setting up
Add Authentication Middleware

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'moe_auth.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
    )
    
Include url

    urlpatterns = patterns('',
        # .......
        url(r'api/',include('moe_auth.api.urls')),
    )

## Related Projects

* [django-rest-auth](https://github.com/bung87/django-rest-auth) if you would like have a registration
  add the url `url(r'^registration/$', include('rest_auth.registration.urls'),name='registration'),`