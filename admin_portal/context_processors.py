# admin_portal/context_processors.py
from django.http import HttpRequest

from admin_portal.registry import admin_menu


def admin_menu_items(request: HttpRequest) -> dict[str, object]:
    return {
        'admin_menu_items': admin_menu.get_items_for_user(request.user),
    }
