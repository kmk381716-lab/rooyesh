from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from home.models import SiteStat


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


class SiteStatForm(forms.ModelForm):

    class Meta:
        model = SiteStat

        fields = (
            "title",
            "value",
            "description",
            "icon",
            "is_active",
            "order",
        )

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً نوجوان فعال"
                }
            ),

            "value": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً 80+"
                }
            ),

            "description": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً اعضای فعال کانون"
                }
            ),

            "icon": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً 👥"
                }
            ),

            "order": forms.NumberInput(
                attrs={
                    "min": 0
                }
            ),
        }