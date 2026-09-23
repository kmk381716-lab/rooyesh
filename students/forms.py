from django import forms

from .models import Student, StudentGroup


class StudentCreateForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = (
            "first_name",
            "last_name",
            "group",
            "phone",
            "parent_phone_1",
            "parent_phone_2",
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

            "group": forms.Select(),

            "phone": forms.TextInput(
                attrs={
                    "placeholder": "شماره تماس دانش‌آموز"
                }
            ),

            "parent_phone_1": forms.TextInput(
                attrs={
                    "placeholder": "شماره تماس والد اول"
                }
            ),

            "parent_phone_2": forms.TextInput(
                attrs={
                    "placeholder": "شماره تماس والد دوم"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["group"].queryset = StudentGroup.objects.filter(
            is_active=True
        ).order_by(
            "name"
        )

        self.fields["group"].empty_label = "انتخاب گروه"


class StudentGroupForm(forms.ModelForm):

    class Meta:
        model = StudentGroup

        fields = (
            "name",
            "is_active",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً نوجوانان"
                }
            ),

            "is_active": forms.CheckboxInput(),
        }