"""
URL configuration for django_forenlims_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching
    path('', include('pages.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('admin/', include('admin_portal.urls', namespace='admin_portal')),
]
