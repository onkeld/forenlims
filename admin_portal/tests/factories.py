import factory

from admin_portal.registry import MenuItem

# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


class MenuItemFactory(factory.Factory):
    """
    Factory for MenuItem — uses factory.Factory (not DjangoModelFactory)
    because MenuItem is a plain dataclass with no database backing.
    """

    class Meta:
        model = MenuItem

    label = factory.Sequence(lambda n: f"Menu Item {n}")
    url_name = factory.Sequence(lambda n: f"app:view_{n}")
    permission = None
    requires_privilege = False
    icon = 'circle'
    order = factory.Sequence(lambda n: n * 10)


class ProtectedMenuItemFactory(MenuItemFactory):
    """A MenuItem that requires a specific permission."""

    permission = 'accounts.view_customuser'


class PrivilegedMenuItemFactory(MenuItemFactory):
    """A MenuItem that requires step-up authentication."""

    requires_privilege = True


class MockUser:
    def __init__(self, permissions: list[str] | None = None) -> None:
        self._permissions = set(permissions or [])

    def has_perm(self, perm: str) -> bool:
        return perm in self._permissions
