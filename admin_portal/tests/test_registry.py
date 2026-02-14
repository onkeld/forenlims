# admin_portal/tests/test_registry.py

import admin_portal.tests.factories as f
from admin_portal.registry import AdminMenuRegistry, MenuItem
from admin_portal.tests.factories import MockUser

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_registry(*items: MenuItem) -> AdminMenuRegistry:
    """Return a fresh registry pre-populated with the given items."""
    registry = AdminMenuRegistry()
    for item in items:
        registry.register(
            label=item.label,
            url_name=item.url_name,
            permission=item.permission,
            requires_privilege=item.requires_privilege,
            icon=item.icon,
            order=item.order,
        )
    return registry


# ---------------------------------------------------------------------------
# MenuItem dataclass
# ---------------------------------------------------------------------------


class TestMenuItem:
    """MenuItem should carry all fields and expose sensible defaults."""

    def test_required_fields_are_stored(self) -> None:
        item = f.MenuItemFactory(
            label='Users', url_name='accounts:admin_user_list'
        )
        assert item.label == 'Users'
        assert item.url_name == 'accounts:admin_user_list'

    def test_permission_defaults_to_none(self) -> None:
        item = f.MenuItemFactory()
        assert item.permission is None

    def test_requires_privilege_defaults_to_false(self) -> None:
        item = f.MenuItemFactory()
        assert item.requires_privilege is False

    def test_icon_has_default(self) -> None:
        item = f.MenuItemFactory()
        assert isinstance(item.icon, str)
        assert len(item.icon) > 0

    def test_order_has_numeric_default(self) -> None:
        item = f.MenuItemFactory()
        assert isinstance(item.order, int)

    def test_all_fields_can_be_set_explicitly(self) -> None:
        item = f.MenuItemFactory(
            label='Users',
            url_name='accounts:admin_user_list',
            permission='accounts.view_customuser',
            requires_privilege=True,
            icon='users',
            order=10,
        )
        assert item.permission == 'accounts.view_customuser'
        assert item.requires_privilege is True
        assert item.icon == 'users'
        assert item.order == 10

    def test_factory_generates_unique_labels(self) -> None:
        items = f.MenuItemFactory.create_batch(3)
        labels = {item.label for item in items}
        assert len(labels) == 3

    def test_factory_generates_unique_url_names(self) -> None:
        items = f.MenuItemFactory.create_batch(3)
        url_names = {item.url_name for item in items}
        assert len(url_names) == 3


# ---------------------------------------------------------------------------
# AdminMenuRegistry — registration
# ---------------------------------------------------------------------------


class TestAdminMenuRegistryRegistration:
    """Items registered with the registry must be retrievable."""

    def test_empty_registry_returns_no_items(self) -> None:
        registry = AdminMenuRegistry()
        user = MockUser()
        assert registry.get_items_for_user(user) == []

    def test_single_item_is_returned(self) -> None:
        item = f.MenuItemFactory(url_name='admin_portal:dashboard')
        registry = make_registry(item)
        user = MockUser()
        result = registry.get_items_for_user(user)
        assert len(result) == 1
        assert result[0].url_name == 'admin_portal:dashboard'

    def test_multiple_items_are_all_registered(self) -> None:
        items = f.MenuItemFactory.create_batch(3)
        registry = make_registry(*items)
        user = MockUser()
        assert len(registry.get_items_for_user(user)) == 3

    def test_registering_same_url_name_twice_creates_two_entries(self) -> None:
        """Registry does not deduplicate — callers are responsible."""
        registry = AdminMenuRegistry()
        for _ in range(2):
            registry.register(
                label='Dashboard', url_name='admin_portal:dashboard'
            )
        user = MockUser()
        assert len(registry.get_items_for_user(user)) == 2


# ---------------------------------------------------------------------------
# AdminMenuRegistry — ordering
# ---------------------------------------------------------------------------


class TestAdminMenuRegistryOrdering:
    """Items must be returned sorted by their order field ascending."""

    def test_items_returned_in_ascending_order(self) -> None:
        item_c = f.MenuItemFactory(url_name='c', order=30)
        item_a = f.MenuItemFactory(url_name='a', order=10)
        item_b = f.MenuItemFactory(url_name='b', order=20)
        registry = make_registry(item_c, item_a, item_b)
        user = MockUser()
        result = registry.get_items_for_user(user)
        assert [i.url_name for i in result] == ['a', 'b', 'c']

    def test_items_registered_in_order_maintain_order(self) -> None:
        item_a = f.MenuItemFactory(url_name='a', order=10)
        item_b = f.MenuItemFactory(url_name='b', order=20)
        registry = make_registry(item_a, item_b)
        user = MockUser()
        result = registry.get_items_for_user(user)
        assert result[0].url_name == 'a'
        assert result[1].url_name == 'b'

    def test_items_with_equal_order_are_both_returned(self) -> None:
        item_a = f.MenuItemFactory(url_name='a', order=10)
        item_b = f.MenuItemFactory(url_name='b', order=10)
        registry = make_registry(item_a, item_b)
        user = MockUser()
        assert len(registry.get_items_for_user(user)) == 2


# ---------------------------------------------------------------------------
# AdminMenuRegistry — permission filtering
# ---------------------------------------------------------------------------


class TestAdminMenuRegistryPermissions:
    """Items with a permission requirement must respect user.has_perm()."""

    def test_item_without_permission_visible_to_any_user(self) -> None:
        item = f.MenuItemFactory()
        registry = make_registry(item)
        user = MockUser(permissions=[])
        assert len(registry.get_items_for_user(user)) == 1

    def test_item_with_permission_hidden_from_unauthorized_user(self) -> None:
        item = f.ProtectedMenuItemFactory()
        registry = make_registry(item)
        user = MockUser(permissions=[])
        assert registry.get_items_for_user(user) == []

    def test_item_with_permission_visible_to_authorized_user(self) -> None:
        item = f.ProtectedMenuItemFactory(
            url_name='accounts:admin_user_list',
            permission='accounts.view_customuser',
        )
        registry = make_registry(item)
        user = MockUser(permissions=['accounts.view_customuser'])
        result = registry.get_items_for_user(user)
        assert len(result) == 1
        assert result[0].url_name == 'accounts:admin_user_list'

    def test_only_permitted_items_returned_in_mixed_list(self) -> None:
        public_item = f.MenuItemFactory(url_name='dashboard')
        user_item = f.ProtectedMenuItemFactory(
            url_name='users',
            permission='accounts.view_customuser',
        )
        audit_item = f.ProtectedMenuItemFactory(
            url_name='audit',
            permission='audittrail.view_logentry',
        )
        registry = make_registry(public_item, user_item, audit_item)
        user = MockUser(permissions=['accounts.view_customuser'])
        result = registry.get_items_for_user(user)
        assert len(result) == 2
        assert {i.url_name for i in result} == {'dashboard', 'users'}

    def test_user_with_all_permissions_sees_all_items(self) -> None:
        public_item = f.MenuItemFactory()
        user_item = f.ProtectedMenuItemFactory(
            permission='accounts.view_customuser'
        )
        audit_item = f.ProtectedMenuItemFactory(
            permission='audittrail.view_logentry'
        )
        registry = make_registry(public_item, user_item, audit_item)
        user = MockUser(
            permissions=[
                'accounts.view_customuser',
                'audittrail.view_logentry',
            ]
        )
        assert len(registry.get_items_for_user(user)) == 3


# ---------------------------------------------------------------------------
# AdminMenuRegistry — requires_privilege flag
# ---------------------------------------------------------------------------


class TestAdminMenuRegistryPrivilegeFlag:
    """
    The registry itself does not enforce privilege — that is the view's job.
    It must however faithfully preserve the flag so views can act on it.
    """

    def test_requires_privilege_false_is_preserved(self) -> None:
        item = f.MenuItemFactory(requires_privilege=False)
        registry = make_registry(item)
        user = MockUser()
        result = registry.get_items_for_user(user)
        assert result[0].requires_privilege is False

    def test_requires_privilege_true_is_preserved(self) -> None:
        item = f.PrivilegedMenuItemFactory()
        registry = make_registry(item)
        user = MockUser()
        result = registry.get_items_for_user(user)
        assert result[0].requires_privilege is True

    def test_privilege_flag_does_not_affect_visibility(self) -> None:
        """
        requires_privilege is orthogonal to permission — both items visible.
        """
        normal_item = f.MenuItemFactory(requires_privilege=False)
        privileged_item = f.PrivilegedMenuItemFactory()
        registry = make_registry(normal_item, privileged_item)
        user = MockUser()
        assert len(registry.get_items_for_user(user)) == 2

    def test_privileged_items_still_respect_permission(self) -> None:
        """requires_privilege and permission are independent filters."""
        item = f.PrivilegedMenuItemFactory(
            permission='accounts.view_customuser'
        )
        registry = make_registry(item)
        unauthorized_user = MockUser(permissions=[])
        authorized_user = MockUser(permissions=['accounts.view_customuser'])
        assert registry.get_items_for_user(unauthorized_user) == []
        assert len(registry.get_items_for_user(authorized_user)) == 1


# ---------------------------------------------------------------------------
# AdminMenuRegistry — isolation between instances
# ---------------------------------------------------------------------------


class TestAdminMenuRegistryIsolation:
    """Each registry instance must have its own independent item list."""

    def test_two_registries_are_independent(self) -> None:
        registry_a = AdminMenuRegistry()
        registry_b = AdminMenuRegistry()
        item = f.MenuItemFactory()
        registry_a.register(label=item.label, url_name=item.url_name)
        user = MockUser()
        assert registry_b.get_items_for_user(user) == []

    def test_registering_in_one_does_not_affect_the_other(self) -> None:
        registry_a = AdminMenuRegistry()
        registry_b = AdminMenuRegistry()
        item_a = f.MenuItemFactory(url_name='a')
        item_b = f.MenuItemFactory(url_name='b')
        registry_a.register(label=item_a.label, url_name=item_a.url_name)
        registry_b.register(label=item_b.label, url_name=item_b.url_name)
        user = MockUser()
        assert len(registry_a.get_items_for_user(user)) == 1
        assert len(registry_b.get_items_for_user(user)) == 1
        assert registry_a.get_items_for_user(user)[0].url_name == 'a'
        assert registry_b.get_items_for_user(user)[0].url_name == 'b'
