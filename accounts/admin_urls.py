#accounts/admin_urls.py
from django.urls import path

from accounts.admin_views import (
    AdminUserCreateView,
    AdminUserDeactivateView,
    AdminUserEditView,
    AdminUserListView,
)

app_name = 'accounts_admin'

urlpatterns = [
    path('accounts/', AdminUserListView.as_view(),
         name='admin_user_list'),
    path('accounts/create/', AdminUserCreateView.as_view(),
         name='admin_user_create'),
    path('accounts/<int:pk>/edit/', AdminUserEditView.as_view(),
         name='admin_user_edit'),
    path('accounts/<int:pk>/deactivate/', AdminUserDeactivateView.as_view(),
         name='admin_user_toggle_active'),
]
