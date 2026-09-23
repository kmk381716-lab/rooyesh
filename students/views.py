from datetime import datetime

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import StudentCreateForm, StudentGroupForm
from .models import Attendance, Student, StudentGroup

def can_manage_students(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name="مربیان").exists()
        )
    )


@user_passes_test(
    can_manage_students,
    login_url="/coaches/login/"
)
def student_list(request):

    students = Student.objects.filter(
        coach=request.user
    )

    return render(
        request,
        "students/student_list.html",
        {
            "students": students
        }
    )

@user_passes_test(
    can_manage_students,
    login_url="/coaches/login/"
)
def student_create(request):

    if request.method == "POST":

        form = StudentCreateForm(request.POST)

        if form.is_valid():

            student = form.save(commit=False)

            student.coach = request.user

            student.save()

            from finance.models import (
                Charge,
                MembershipFeeSetting,
            )

            setting = MembershipFeeSetting.objects.filter(
                is_active=True
            ).order_by(
                "-updated_at"
            ).first()

            if setting and setting.amount > 0:

                Charge.objects.create(
                    student=student,
                    charge_type="membership",
                    title="حق عضویت",
                    amount=setting.amount,
                    description="حق عضویت بر اساس مبلغ تعیین‌شده توسط مدیر اصلی.",
                    created_by=request.user,
                )

            return redirect(
                "students:list"
            )

    else:

        form = StudentCreateForm()

    return render(
        request,
        "students/student_create.html",
        {
            "form": form
        }
    )

@user_passes_test(
    can_manage_students,
    login_url="/coaches/login/"
)
def student_detail(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id,
        coach=request.user
    )

    attendances = Attendance.objects.filter(
        student=student
    ).order_by(
        "-date"
    )

    summary = attendances.aggregate(
        total=Count("id"),

        present=Count(
            "id",
            filter=Q(status="present")
        ),

        absent=Count(
            "id",
            filter=Q(status="absent")
        ),

        excused=Count(
            "id",
            filter=Q(status="excused")
        ),

        heyat=Count(
            "id",
            filter=Q(attendance_type="heyat")
        ),

        weekly_class=Count(
            "id",
            filter=Q(attendance_type="weekly_class")
        ),

        meeting=Count(
            "id",
            filter=Q(attendance_type="meeting")
        ),
    )

    type_summary = {
        "heyat": attendances.filter(
            attendance_type="heyat"
        ).aggregate(
            total=Count("id"),
            present=Count(
                "id",
                filter=Q(status="present")
            ),
            absent=Count(
                "id",
                filter=Q(status="absent")
            ),
            excused=Count(
                "id",
                filter=Q(status="excused")
            ),
        ),

        "weekly_class": attendances.filter(
            attendance_type="weekly_class"
        ).aggregate(
            total=Count("id"),
            present=Count(
                "id",
                filter=Q(status="present")
            ),
            absent=Count(
                "id",
                filter=Q(status="absent")
            ),
            excused=Count(
                "id",
                filter=Q(status="excused")
            ),
        ),

        "meeting": attendances.filter(
            attendance_type="meeting"
        ).aggregate(
            total=Count("id"),
            present=Count(
                "id",
                filter=Q(status="present")
            ),
            absent=Count(
                "id",
                filter=Q(status="absent")
            ),
            excused=Count(
                "id",
                filter=Q(status="excused")
            ),
        ),
    }

    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "attendances": attendances,
            "summary": summary,
            "type_summary": type_summary,
        }
    )
@user_passes_test(
    can_manage_students,
    login_url="/coaches/login/"
)
def attendance_create(request):

    students = Student.objects.filter(
        coach=request.user,
        is_active=True
    ).order_by(
        "first_name",
        "last_name"
    )

    if request.method == "POST":

        attendance_type = request.POST.get(
            "attendance_type"
        )

        attendance_date = request.POST.get(
            "date"
        )

        title = request.POST.get(
            "title",
            ""
        ).strip()

        valid_types = {
            "heyat",
            "weekly_class",
            "meeting",
        }

        if attendance_type not in valid_types:

            return render(
                request,
                "students/attendance_create.html",
                {
                    "students": students,
                    "error": "نوع برنامه نامعتبر است.",
                    "today": timezone.localdate(),
                }
            )

        try:

            attendance_date = datetime.strptime(
                attendance_date,
                "%Y-%m-%d"
            ).date()

        except (TypeError, ValueError):

            return render(
                request,
                "students/attendance_create.html",
                {
                    "students": students,
                    "error": "تاریخ وارد شده صحیح نیست.",
                    "today": timezone.localdate(),
                }
            )

        for student in students:

            status = request.POST.get(
                f"status_{student.id}"
            )

            if status not in {
                "present",
                "absent",
                "excused",
            }:
                continue

            Attendance.objects.update_or_create(

                student=student,

                attendance_type=attendance_type,

                date=attendance_date,

                defaults={
                    "status": status,
                    "title": title,
                }

            )

        return redirect(
            "students:attendance_create"
        )

    return render(
        request,
        "students/attendance_create.html",
        {
            "students": students,
            "today": timezone.localdate(),
        }
    )


@user_passes_test(
    can_manage_students,
    login_url="/coaches/login/"
)
def student_delete(request, student_id):

    if request.method != "POST":

        return redirect(
            "students:list"
        )

    student = get_object_or_404(
        Student,
        id=student_id,
        coach=request.user
    )

    student.delete()

    return redirect(
        "students:list"
    )

@user_passes_test(
    lambda user: user.is_authenticated and user.is_superuser,
    login_url="/coaches/login/"
)
def group_management(request):

    groups = StudentGroup.objects.all()

    return render(
        request,
        "students/group_management.html",
        {
            "groups": groups
        }
    )


@user_passes_test(
    lambda user: user.is_authenticated and user.is_superuser,
    login_url="/coaches/login/"
)
def group_create(request):

    if request.method == "POST":

        form = StudentGroupForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "students:group_management"
            )

    else:

        form = StudentGroupForm()

    return render(
        request,
        "students/group_form.html",
        {
            "form": form,
            "title": "افزودن گروه"
        }
    )


@user_passes_test(
    lambda user: user.is_authenticated and user.is_superuser,
    login_url="/coaches/login/"
)
def group_edit(request, group_id):

    group = get_object_or_404(
        StudentGroup,
        id=group_id
    )

    if request.method == "POST":

        form = StudentGroupForm(
            request.POST,
            instance=group
        )

        if form.is_valid():

            form.save()

            return redirect(
                "students:group_management"
            )

    else:

        form = StudentGroupForm(
            instance=group
        )

    return render(
        request,
        "students/group_form.html",
        {
            "form": form,
            "title": "ویرایش گروه"
        }
    )


@user_passes_test(
    lambda user: user.is_authenticated and user.is_superuser,
    login_url="/coaches/login/"
)
def group_toggle(request, group_id):

    if request.method != "POST":

        return redirect(
            "students:group_management"
        )

    group = get_object_or_404(
        StudentGroup,
        id=group_id
    )

    group.is_active = not group.is_active

    group.save(
        update_fields=["is_active"]
    )

    return redirect(
        "students:group_management"
    )
@user_passes_test(
    lambda user: user.is_authenticated and user.is_superuser,
    login_url="/coaches/login/"
)
def all_students(request):

    groups = StudentGroup.objects.prefetch_related(
        "students__coach"
    ).all()

    ungrouped_students = Student.objects.filter(
        group__isnull=True
    ).select_related(
        "coach"
    ).order_by(
        "first_name",
        "last_name"
    )

    return render(
        request,
        "students/all_students.html",
        {
            "groups": groups,
            "ungrouped_students": ungrouped_students,
        }
    )