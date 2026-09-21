from django import forms


class ExcelImportForm(forms.Form):

    excel_file = forms.FileField(
        label="فایل اکسل",
        help_text="فقط فایل .xlsx"
    )

    def clean_excel_file(self):
        file = self.cleaned_data["excel_file"]

        if not file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError(
                "فقط فایل Excel با پسوند .xlsx قابل قبول است."
            )

        return file