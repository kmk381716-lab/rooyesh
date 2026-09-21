from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.shortcuts import get_object_or_404, render, redirect
from .models import Answer, Form, Option, Question, Submission
from django.shortcuts import (
    get_object_or_404,
    render,
    redirect,
)

FIELD_TYPES = {
    "text": "متن کوتاه",
    "textarea": "متن بلند",
    "number": "عدد",
    "boolean": "بله / خیر",
    "single": "تک‌انتخابی",
    "multiple": "چندانتخابی",
    "date": "تاریخ",
    "file": "فایل",
}


# =========================================================
# ساخت فرم
# =========================================================

@staff_member_required
def builder(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        if not title:
            return render(
                request,
                "forms/builder.html",
                {
                    "field_types": FIELD_TYPES,
                    "error": "عنوان فرم را وارد کنید.",
                },
            )

        question_keys = request.POST.getlist(
            "question_key"
        )

        question_titles = request.POST.getlist(
            "question_title"
        )

        question_types = request.POST.getlist(
            "question_type"
        )

        question_required = request.POST.getlist(
            "question_required"
        )

        with transaction.atomic():

            form = Form.objects.create(
                title=title,
                description=description,
                created_by=request.user,
            )

            for index, question_title in enumerate(
                question_titles
            ):

                question_title = question_title.strip()

                if not question_title:
                    continue

                if index < len(question_keys):
                    key = question_keys[index]
                else:
                    key = str(index)

                if index < len(question_types):
                    field_type = question_types[index]
                else:
                    field_type = "text"

                if field_type not in FIELD_TYPES:
                    field_type = "text"

                required = key in question_required

                question = Question.objects.create(
                    form=form,
                    title=question_title,
                    field_type=field_type,
                    required=required,
                    order=index,
                )

                # گزینه‌ها فقط برای سوالات انتخابی
                if field_type in [
                    "single",
                    "multiple",
                ]:

                    option_name = f"option_{key}"

                    options = request.POST.getlist(
                        option_name
                    )

                    for option_index, option_title in enumerate(
                        options
                    ):

                        option_title = option_title.strip()

                        if not option_title:
                            continue

                        Option.objects.create(
                            question=question,
                            title=option_title,
                            order=option_index,
                        )

        # صفحه مخصوص سازنده فرم
        return render(
            request,
            "forms/builder_success.html",
            {
                "form": form,
            },
        )

    return render(
        request,
        "forms/builder.html",
        {
            "field_types": FIELD_TYPES,
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
        .filter(is_active=True)
        .order_by("-created_at")
    )

    return render(
        request,
        "forms/form_list.html",
        {
            "forms": forms,
        },
    )


# =========================================================
# پر کردن فرم
# عمومی
# =========================================================

def fill_form(request, form_id):

    form = get_object_or_404(
        Form.objects.prefetch_related(
            "questions__options"
        ),
        id=form_id,
        is_active=True,
    )

    questions = form.questions.all().order_by(
        "order"
    )

    if request.method == "POST":

        errors = {}

        # -------------------------------------------------
        # بررسی پاسخ‌ها
        # -------------------------------------------------

        for question in questions:

            field_name = f"question_{question.id}"

            # ---------------------------------------------
            # متن کوتاه، متن بلند، عدد، تاریخ
            # ---------------------------------------------

            if question.field_type in [
                "text",
                "textarea",
                "number",
                "date",
            ]:

                value = request.POST.get(
                    field_name,
                    "",
                ).strip()

                if question.required and not value:
                    errors[question.id] = (
                        "این سؤال اجباری است."
                    )

            # ---------------------------------------------
            # بله / خیر
            # ---------------------------------------------

            elif question.field_type == "boolean":

                value = request.POST.get(
                    field_name,
                    "",
                ).strip()

                if value not in [
                    "",
                    "بله",
                    "خیر",
                ]:

                    errors[question.id] = (
                        "پاسخ این سؤال معتبر نیست."
                    )

                elif question.required and not value:

                    errors[question.id] = (
                        "این سؤال اجباری است."
                    )

            # ---------------------------------------------
            # تک انتخابی
            # ---------------------------------------------

            elif question.field_type == "single":

                value = request.POST.get(
                    field_name,
                    "",
                ).strip()

                valid_values = set(
                    question.options.values_list(
                        "title",
                        flat=True,
                    )
                )

                if value and value not in valid_values:

                    errors[question.id] = (
                        "گزینه انتخاب‌شده معتبر نیست."
                    )

                elif question.required and not value:

                    errors[question.id] = (
                        "این سؤال اجباری است."
                    )

            # ---------------------------------------------
            # چند انتخابی
            # ---------------------------------------------

            elif question.field_type == "multiple":

                values = request.POST.getlist(
                    field_name
                )

                valid_values = set(
                    question.options.values_list(
                        "title",
                        flat=True,
                    )
                )

                invalid_values = [
                    value
                    for value in values
                    if value not in valid_values
                ]

                if invalid_values:

                    errors[question.id] = (
                        "یکی از گزینه‌های انتخاب‌شده معتبر نیست."
                    )

                elif question.required and not values:

                    errors[question.id] = (
                        "این سؤال اجباری است."
                    )

            # ---------------------------------------------
            # فایل
            # ---------------------------------------------

            elif question.field_type == "file":

                uploaded_file = request.FILES.get(
                    field_name
                )

                if question.required and not uploaded_file:

                    errors[question.id] = (
                        "این فایل اجباری است."
                    )

        # -------------------------------------------------
        # اگر خطا داشتیم
        # -------------------------------------------------

        if errors:

            return render(
                request,
                "forms/form_fill.html",
                {
                    "form": form,
                    "questions": questions,
                    "errors": errors,
                },
            )

        # -------------------------------------------------
        # ذخیره پاسخ
        # -------------------------------------------------

        with transaction.atomic():

            submission = Submission.objects.create(
                form=form,
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
            )

            for question in questions:

                field_name = f"question_{question.id}"

                # چند انتخابی
                if question.field_type == "multiple":

                    values = request.POST.getlist(
                        field_name
                    )

                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        text_value=",".join(values),
                    )

                # فایل
                elif question.field_type == "file":

                    uploaded_file = request.FILES.get(
                        field_name
                    )

                    if uploaded_file:

                        Answer.objects.create(
                            submission=submission,
                            question=question,
                            file_value=uploaded_file,
                        )

                # بقیه انواع
                else:

                    value = request.POST.get(
                        field_name,
                        "",
                    ).strip()

                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        text_value=value,
                    )

        # صفحه مخصوص کسی که فرم را پر کرده
        return render(
            request,
            "forms/submission_success.html",
            {
                "form": form,
            },
        )

    return render(
        request,
        "forms/form_fill.html",
        {
            "form": form,
            "questions": questions,
            "errors": {},
        },
    )


# =========================================================
# داشبورد پاسخ‌ها
# فقط Staff
# =========================================================

@staff_member_required
def response_dashboard(request):

    forms = (
        Form.objects
        .all()
        .order_by("-created_at")
    )

    submissions = (
        Submission.objects
        .select_related(
            "form",
            "user",
        )
        .prefetch_related(
            "answers__question",
        )
        .order_by("-created_at")
    )

    # -------------------------------------------------
    # فیلتر فرم
    # -------------------------------------------------

    selected_form = request.GET.get(
        "form",
        "",
    ).strip()

    selected_form_id = None

    if selected_form:

        try:

            selected_form_id = int(
                selected_form
            )

            submissions = submissions.filter(
                form_id=selected_form_id
            )

        except ValueError:

            selected_form_id = None

    # -------------------------------------------------
    # جستجو
    # -------------------------------------------------

    search = request.GET.get(
        "q",
        "",
    ).strip()

    if search:

        query = (
            Q(form__title__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(answers__text_value__icontains=search)
        )

        submissions = (
            submissions
            .filter(query)
            .distinct()
        )

    # -------------------------------------------------
    # آمار
    # -------------------------------------------------

    total_forms = Form.objects.count()

    total_submissions = Submission.objects.count()

    # -------------------------------------------------
    # صفحه‌بندی
    # -------------------------------------------------

    paginator = Paginator(
        submissions,
        20,
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

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
def submission_detail(
    request,
    submission_id,
):

    submission = get_object_or_404(
        Submission.objects
        .select_related(
            "form",
            "user",
        )
        .prefetch_related(
            "answers__question",
        ),
        id=submission_id,
    )

    answers = (
        submission.answers
        .all()
        .order_by(
            "question__order"
        )
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
# حذف پاسخ
# فقط Staff
# =========================================================
@staff_member_required
def delete_form(request, form_id):

    if request.method == "POST":

        Form.objects.filter(
            id=form_id
        ).delete()

        return redirect(
            "forms:form_list"
        )

    form = get_object_or_404(
        Form,
        id=form_id,
    )

    return render(
        request,
        "forms/delete_form.html",
        {
            "form": form,
        },
    )
@staff_member_required
def delete_submission(request, submission_id):

    submission = get_object_or_404(
        Submission,
        id=submission_id,
    )

    if request.method == "POST":

        submission.delete()

        return redirect(
            "forms:responses"
        )

    return render(
        request,
        "forms/delete_submission.html",
        {
            "submission": submission,
        },
    )