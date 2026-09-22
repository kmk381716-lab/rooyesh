from datetime import datetime
from django.db.models import Count, Q
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import StudentCreateForm
from .models import Attendance, Student


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
