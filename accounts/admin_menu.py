# accounts/admin_menu.py
from django.utils.translation import gettext as _

from admin_portal.registry import admin_menu

admin_menu.register(
    label=_('User Management'),
    url_name='admin_portal:accounts_admin:admin_user_list',
    permission='accounts.view_customuser',
    icon='users',
    order=10,
)
