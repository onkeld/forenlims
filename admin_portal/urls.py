from django.urls import include, path

from .views import DashboardView

app_name = 'admin_portal'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('accounts/', include('accounts.admin_urls'))
]
