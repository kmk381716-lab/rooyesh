from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.contrib import messages

from students.models import Student

from .forms import (
    ChargeForm,
    MembershipFeeSettingForm,
    PaymentForm,
)

from .models import (
    Charge,
    MembershipFeeSetting,
)


def is_manager(user):

    return (
        user.is_authenticated
        and user.is_superuser
    )


def can_manage_finance(user):

    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(
                name="مربیان"
            ).exists()
        )
    )


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def membership_fee(request):

    setting = MembershipFeeSetting.objects.order_by(
        "-updated_at"
    ).first()

    if request.method == "POST":

        form = MembershipFeeSettingForm(
            request.POST,
            instance=setting
        )

        if form.is_valid():

            form.save()

            return redirect(
                "finance:membership_fee"
            )

    else:

        form = MembershipFeeSettingForm(
            instance=setting
        )

    return render(
        request,
        "finance/membership_fee.html",
        {
            "form": form,
            "setting": setting,
        }
    )


@user_passes_test(
    can_manage_finance,
    login_url="/coaches/login/"
)
def charge_create(request):

    if request.method == "POST":

        form = ChargeForm(
            request.user,
            request.POST
        )

        # 🔍 دیباگ — این خطا رو تو ترمینال چاپ می‌کنه
        print("=" * 50)
        print("POST DATA:", dict(request.POST))
        print("FORM VALID:", form.is_valid())
        if not form.is_valid():
            print("FORM ERRORS:", form.errors)
        print("=" * 50)

        if form.is_valid():

            charge = form.save(commit=False)

            charge.created_by = request.user

            charge.save()

            # ✅ پیام موفقیت
            messages.success(
                request,
                f"بدهی «{charge.title}» با موفقیت برای {charge.student} ثبت شد."
            )

            # ✅ برگرد به داشبورد (نه به همین صفحه)
            return redirect("coaches:dashboard")

    else:

        form = ChargeForm(request.user)

    return render(
        request,
        "finance/charge_create.html",
        {"form": form}
    )

@user_passes_test(
    can_manage_finance,
    login_url="/coaches/login/"
)
def student_finance(request, student_id):

    if request.user.is_superuser:

        student = get_object_or_404(
            Student,
            id=student_id
        )

    else:

        student = get_object_or_404(
            Student,
            id=student_id,
            coach=request.user
        )

    charges = Charge.objects.filter(
        student=student
    ).prefetch_related(
        "payments"
    ).order_by(
        "-created_at"
    )

    total_charges = charges.aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_payments = 0

    for charge in charges:

        total_payments += sum(
            payment.amount
            for payment in charge.payments.all()
        )

    remaining = max(
        total_charges - total_payments,
        0
    )

    return render(
        request,
        "finance/student_finance.html",
        {
            "student": student,
            "charges": charges,
            "total_charges": total_charges,
            "total_payments": total_payments,
            "remaining": remaining,
        }
    )


@user_passes_test(
    can_manage_finance,
    login_url="/coaches/login/"
)
def payment_create(request, charge_id):

    if request.user.is_superuser:

        charge = get_object_or_404(
            Charge,
            id=charge_id
        )

    else:

        charge = get_object_or_404(
            Charge,
            id=charge_id,
            student__coach=request.user
        )

    remaining = charge.remaining_amount

    if remaining <= 0:

        return redirect(
            "finance:student_finance",
            student_id=charge.student.id
        )

    if request.method == "POST":

        form = PaymentForm(
            request.POST
        )

        if form.is_valid():

            payment_amount = form.cleaned_data["amount"]

            if payment_amount > remaining:

                form.add_error(
                    "amount",
                    "مبلغ پرداخت نمی‌تواند بیشتر از مانده بدهی باشد."
                )

            else:

                payment = form.save(
                    commit=False
                )

                payment.charge = charge
                payment.created_by = request.user

                payment.save()

                return redirect(
                    "finance:student_finance",
                    student_id=charge.student.id
                )

    else:

        form = PaymentForm()

    return render(
        request,
        "finance/payment_create.html",
        {
            "form": form,
            "charge": charge,
            "remaining": remaining,
        }
    )

@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def apply_membership_fee(request):

    if request.method != "POST":

        return redirect(
            "finance:membership_fee"
        )

    setting = MembershipFeeSetting.objects.filter(
        is_active=True
    ).order_by(
        "-updated_at"
    ).first()

    if setting is None:

        messages.error(
            request,
            "ابتدا مبلغ حق عضویت را تعیین و فعال کنید."
        )

        return redirect(
            "finance:membership_fee"
        )

    if setting.amount <= 0:

        messages.error(
            request,
            "مبلغ حق عضویت باید بیشتر از صفر باشد."
        )

        return redirect(
            "finance:membership_fee"
        )

    students = Student.objects.filter(
        is_active=True
    )

    created_count = 0
    existing_count = 0

    for student in students:

        membership_exists = Charge.objects.filter(
            student=student,
            charge_type="membership"
        ).exists()

        if membership_exists:

            existing_count += 1

            continue

        Charge.objects.create(
            student=student,
            charge_type="membership",
            title="حق عضویت",
            amount=setting.amount,
            description="حق عضویت بر اساس مبلغ تعیین‌شده توسط مدیر اصلی.",
            created_by=request.user,
        )

        created_count += 1

    messages.success(
        request,
        (
            f"{created_count} حق عضویت ایجاد شد. "
            f"{existing_count} دانش‌آموز از قبل حق عضویت داشتند."
        )
    )

    return redirect(
        "finance:membership_fee"
    )