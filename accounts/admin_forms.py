# accounts/admin_forms.py
from django import forms

from accounts.models import CustomUser


class AdminUserCreateForm(forms.ModelForm):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

class AdminUserEditForm(forms.ModelForm):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'is_active', 'is_staff']
