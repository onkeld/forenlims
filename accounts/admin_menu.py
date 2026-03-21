# accounts/admin_menu.py
from admin_portal.registry import admin_menu

admin_menu.register(
    label='Benutzerverwaltung',
    url_name='admin_portal:accounts_admin:admin_user_list',
    permission='accounts.view_customuser',
    icon='users',
    order=10,
)
