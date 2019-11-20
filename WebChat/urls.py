"""bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from webapp.views import *
urlpatterns = [
    url(r'^$',index,name="Home"),
    url(r'^webhook', web_hook, name="webhook"),
    url(r'^accounts/',include([
        url(r'^login/$',login_user,name="login"),
        url(r'^logout/$',logout_user, name="logout")
        ])),
    url(r'^admin/', admin.site.urls),
]
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import settings
if settings.DEBUG == True:
    urlpatterns += staticfiles_urlpatterns()
