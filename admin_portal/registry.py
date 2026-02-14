# admin_portal/registry.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MenuItem:
    label: str
    url_name: str
    permission: str | None = None
    requires_privilege: bool = False
    icon: str = 'circle'
    order: int = 100


class AdminMenuRegistry:
    name = 'Admin Menu Registry'

    def __init__(self) -> None:
        self._items: list[MenuItem] = []

    def register(self, **kwargs: object) -> None:
        self._items.append(MenuItem(**kwargs))

    def get_items_for_user(self, user: object) -> list[MenuItem]:
        visible = [
            item
            for item in self._items
            if item.permission is None or user.has_perm(item.permission)
        ]
        return sorted(visible, key=lambda item: item.order)


admin_menu = AdminMenuRegistry()
