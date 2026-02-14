import factory
from factory.django import DjangoModelFactory
from faker import Faker

from accounts.models import CustomUser

fake = Faker()


class CustomUserFactory(DjangoModelFactory):
    """Factory for creating CustomUser instances in tests."""

    class Meta:
        model = CustomUser
        django_get_or_create = ('email',)
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(
        self,
        create: bool,
        extracted: str | None,
        **_kwargs: object,
    ) -> None:
        """Set password after user creation."""
        if not create:
            return

        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('defaultpass123')
            self.save()


class StaffUserFactory(CustomUserFactory):
    """Factory for creating staff users."""

    is_staff = True


class SuperUserFactory(CustomUserFactory):
    """Factory for creating superusers."""

    is_staff = True
    is_superuser = True
