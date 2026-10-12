from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.core.validators import FileExtensionValidator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Answer, Form, Option, Question, Submission


# =========================================================
# ساخت فرم داینامیک بر اساس سؤالات
# =========================================================
def build_dynamic_form(questions):
    """
    برای هر سؤال یک فیلد مناسب در فرم جنگو می‌سازد.
    """
    fields = {}

    for q in questions:
        name = f"question_{q.id}"

        if q.field_type == Question.FieldType.TEXT:
            fields[name] = forms.CharField(
                label=q.title,
                required=q.required,
                max_length=500,
            )

        elif q.field_type == Question.FieldType.TEXTAREA:
            fields[name] = forms.CharField(
                label=q.title,
                required=q.required,
                widget=forms.Textarea(attrs={"rows": 4}),
            )

        elif q.field_type == Question.FieldType.NUMBER:
            fields[name] = forms.DecimalField(
                label=q.title,
                required=q.required,
                max_digits=15,
                decimal_places=3,
            )

        elif q.field_type == Question.FieldType.BOOLEAN:
            fields[name] = forms.ChoiceField(
                label=q.title,
                required=q.required,
                choices=[
                    ("true", "بله"),
                    ("false", "خیر"),
                ],
                widget=forms.RadioSelect,
            )

        elif q.field_type == Question.FieldType.DATE:
            fields[name] = forms.DateField(
                label=q.title,
                required=q.required,
                widget=forms.DateInput(
                    attrs={"type": "date"},
                    format="%Y-%m-%d",
                ),
                input_formats=["%Y-%m-%d"],
            )

        elif q.field_type == Question.FieldType.FILE:
            fields[name] = forms.FileField(
                label=q.title,
                required=q.required,
                validators=[
                    FileExtensionValidator(
                        allowed_extensions=[
                            "pdf", "jpg", "jpeg", "png",
                            "doc", "docx", "xls", "xlsx", "zip",
                        ]
                    )
                ],
            )

        elif q.field_type == Question.FieldType.SINGLE:
            fields[name] = forms.ModelChoiceField(
                label=q.title,
                required=q.required,
                queryset=q.options.all(),
                empty_label=None if q.required else "---------",
                widget=forms.RadioSelect,
            )

        elif q.field_type == Question.FieldType.MULTIPLE:
            fields[name] = forms.ModelMultipleChoiceField(
                label=q.title,
                required=q.required,
                queryset=q.options.all(),
                widget=forms.CheckboxSelectMultiple,
            )

    return type("DynamicForm", (forms.Form,), fields)


# =========================================================
# ساخت فرم (Builder)
# فقط Staff
# =========================================================
@staff_member_required
def builder(request):

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        if not title:
            return render(
                request,
                "forms/builder.html",
                {
                    "field_types": Question.FieldType.choices,
                    "error": "عنوان فرم را وارد کنید.",
                    "posted": request.POST,
                },
            )

        question_keys = request.POST.getlist("question_key")

        with transaction.atomic():

            form = Form.objects.create(
                title=title,
                description=description,
                created_by=request.user,
            )

            for order_index, key in enumerate(question_keys):

                question_title = request.POST.get(
                    f"question_title_{key}", ""
                ).strip()

                if not question_title:
                    continue

                field_type = request.POST.get(
                    f"question_type_{key}", Question.FieldType.TEXT
                )

                valid_types = {t[0] for t in Question.FieldType.choices}
                if field_type not in valid_types:
                    field_type = Question.FieldType.TEXT

                required = f"question_required_{key}" in request.POST

                question = Question.objects.create(
                    form=form,
                    title=question_title,
                    field_type=field_type,
                    required=required,
                    order=order_index,
                )

                if field_type in (
                    Question.FieldType.SINGLE,
                    Question.FieldType.MULTIPLE,
                ):
                    options = request.POST.getlist(f"option_{key}")

                    for option_index, option_title in enumerate(options):
                        option_title = option_title.strip()
                        if not option_title:
                            continue

                        Option.objects.create(
                            question=question,
                            title=option_title,
                            order=option_index,
                        )

        return redirect("forms:builder_success", form_uuid=form.uuid)

    return render(
        request,
        "forms/builder.html",
        {
            "field_types": Question.FieldType.choices,
        },
    )


# =========================================================
# صفحه موفقیت ساخت فرم
# =========================================================
@staff_member_required
def builder_success(request, form_uuid):

    form = get_object_or_404(Form, uuid=form_uuid)
    fill_url = request.build_absolute_uri(
        reverse("forms:fill_form", kwargs={"form_uuid": form.uuid})
    )

    return render(
        request,
        "forms/builder_success.html",
        {
            "form": form,
            "fill_url": fill_url,
        },
    )


# =========================================================
# لیست فرم‌ها
# فقط Staff
# =========================================================
@staff_member_required
def form_list(request):

    forms = (
        Form.objects
        .select_related("created_by")
        .filter(is_active=True)
        .order_by("-created_at")
    )

    return render(
        request,
        "forms/form_list.html",
        {"forms": forms},
    )


# =========================================================
# پر کردن فرم
# عمومی
# =========================================================
def fill_form(request, form_uuid):
    form = get_object_or_404(
        Form.objects.prefetch_related("questions__options"),
        uuid=form_uuid,
        is_active=True,
    )

    questions = list(
        form.questions.prefetch_related("options").order_by("order")
    )

    DynamicForm = build_dynamic_form(questions)

    if request.method == "POST":

        form_obj = DynamicForm(request.POST, request.FILES)

        if form_obj.is_valid():

            with transaction.atomic():

                submission = Submission.objects.create(
                    form=form,
                    user=(
                        request.user
                        if request.user.is_authenticated
                        else None
                    ),
                )

                for q in questions:

                    name = f"question_{q.id}"
                    value = form_obj.cleaned_data.get(name)

                    if value in (None, "", []):
                        continue

                    answer = Answer(submission=submission, question=q)

                    if q.field_type in ("text", "textarea"):
                        answer.text_value = value

                    elif q.field_type == "number":
                        answer.number_value = value

                    elif q.field_type == "date":
                        answer.date_value = value

                    elif q.field_type == "boolean":
                        answer.boolean_value = (value == "true")

                    elif q.field_type == "file":
                        answer.file_value = value

                    elif q.field_type in ("single", "multiple"):
                        answer.save()
                        if q.field_type == "single":
                            answer.selected_options.set([value])
                        else:
                            answer.selected_options.set(value)
                        continue

                    answer.save()

            return redirect(
                "forms:submission_success",
                form_uuid=form.uuid,
            )

    else:
        form_obj = DynamicForm()

    # ⚠️ این بخش مهمه — جفت کردن سؤال و فیلد
    fields_by_question = []
    for q in questions:
        field_name = f"question_{q.id}"
        fields_by_question.append((q, form_obj[field_name]))

    return render(
        request,
        "forms/form_fill.html",
        {
            "form": form,
            "form_obj": form_obj,
            "questions": questions,
            "fields_by_question": fields_by_question,  # ← این خط حیاتیه
        },
    )


# =========================================================
# صفحه موفقیت ثبت پاسخ
# =========================================================
def submission_success(request, form_uuid):

    form = get_object_or_404(Form, uuid=form_uuid)

    return render(
        request,
        "forms/submission_success.html",
        {"form": form},
    )

# =========================================================
# داشبورد پاسخ‌ها
# فقط Staff
# =========================================================
@staff_member_required
def response_dashboard(request):

    forms = Form.objects.all().order_by("-created_at")

    submissions = (
        Submission.objects
        .select_related("form", "user")
        .prefetch_related("answers__question")
        .order_by("-created_at")
    )

    # ---- فیلتر فرم ----
    selected_form_id = request.GET.get("form", "").strip()

    if selected_form_id:
        try:
            selected_form_id = int(selected_form_id)
            submissions = submissions.filter(form_id=selected_form_id)
        except ValueError:
            selected_form_id = None
    else:
        selected_form_id = None

    # ---- جستجو ----
    search = request.GET.get("q", "").strip()

    if search:
        submissions = submissions.filter(
            Q(form__title__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(answers__text_value__icontains=search)
            | Q(answers__selected_options__title__icontains=search)
        ).distinct()

    # ---- آمار ----
    total_forms = Form.objects.count()
    total_submissions = Submission.objects.count()

    # ---- صفحه‌بندی ----
    paginator = Paginator(submissions, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "forms/responses.html",
        {
            "forms": forms,
            "page_obj": page_obj,
            "total_forms": total_forms,
            "total_submissions": total_submissions,
            "selected_form_id": selected_form_id,
            "search": search,
        },
    )


# =========================================================
# جزئیات یک پاسخ
# فقط Staff
# =========================================================
@staff_member_required
def submission_detail(request, submission_id):

    submission = get_object_or_404(
        Submission.objects
        .select_related("form", "user")
        .prefetch_related(
            "answers__question",
            "answers__selected_options",
        ),
        id=submission_id,
    )

    answers = (
        submission.answers
        .select_related("question")
        .prefetch_related("selected_options")
        .order_by("question__order")
    )

    return render(
        request,
        "forms/submission_detail.html",
        {
            "submission": submission,
            "answers": answers,
        },
    )


# =========================================================
# حذف فرم
# فقط Staff و فقط سازنده یا سوپریوزر
# =========================================================
@staff_member_required
def delete_form(request, form_id):

    form = get_object_or_404(Form, id=form_id)

    if not request.user.is_superuser and form.created_by != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form.delete()
        return redirect("forms:form_list")

    return render(
        request,
        "forms/delete_form.html",
        {"form": form},
    )


# =========================================================
# حذف پاسخ
# فقط Staff
# =========================================================
@staff_member_required
def delete_submission(request, submission_id):

    submission = get_object_or_404(Submission, id=submission_id)

    if request.method == "POST":
        submission.delete()
        return redirect("forms:responses")

    return render(
        request,
        "forms/delete_submission.html",
        {"submission": submission},
    )