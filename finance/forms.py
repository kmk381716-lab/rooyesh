from django import forms

from students.models import Student

from .models import (
    Charge,
    MembershipFeeSetting,
    Payment,
)


class MembershipFeeSettingForm(forms.ModelForm):

    class Meta:
        model = MembershipFeeSetting

        fields = (
            "amount",
            "is_active",
        )

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "مثلاً 500000",
                    "min": "0",
                }
            ),

            "is_active": forms.CheckboxInput(),
        }


class ChargeForm(forms.ModelForm):

    class Meta:
        model = Charge

        fields = (
            "student",
            "charge_type",
            "title",
            "amount",
            "description",
        )

        widgets = {
            "student": forms.Select(),

            "charge_type": forms.Select(),

            "title": forms.TextInput(
                attrs={
                    "placeholder": "مثلاً اردوی قم"
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "مثلاً 800000",
                    "min": "1",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "توضیحات اختیاری",
                    "rows": 4,
                }
            ),
        }

    def __init__(
        self,
        user,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        if user.is_superuser:

            students = Student.objects.all()

        else:

            students = Student.objects.filter(
                coach=user
            )

        self.fields["student"].queryset = students.order_by(
            "first_name",
            "last_name"
        )

        self.fields["student"].empty_label = "انتخاب دانش‌آموز"


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment

        fields = (
            "amount",
            "description",
        )

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "مثلاً 300000",
                    "min": "1",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "توضیحات اختیاری",
                    "rows": 3,
                }
            ),
        }