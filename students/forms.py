from django import forms

from .models import Student


class StudentCreateForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = (
            "first_name",
            "last_name",
            "grade",
            "phone",
            "parent_phone",
        )

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "نام دانش‌آموز"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "نام خانوادگی"
                }
            ),

            "grade": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً هشتم"
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "شماره تماس دانش‌آموز"
                }
            ),

            "parent_phone": forms.TextInput(
                attrs={
                    "placeholder": "شماره تماس والدین"
                }
            ),
        }