from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CoachCreateForm(UserCreationForm):

    first_name = forms.CharField(
        label="نام",
        max_length=150,
        required=True
    )

    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=150,
        required=True
    )

    email = forms.EmailField(
        label="ایمیل",
        required=False
    )

    class Meta:
        model = User

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )