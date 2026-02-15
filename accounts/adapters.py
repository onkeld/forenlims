from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpRequest


class NoSignupAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> dict[str, object]:
        """
        Not open for signup.
        """
        return False
