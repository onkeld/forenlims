# accounts/forms.py
from django import forms

from accounts.models import CustomUser


class UserEditForm(forms.ModelForm):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']
