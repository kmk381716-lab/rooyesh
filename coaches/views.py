from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404, redirect, render

from home.models import SiteStat

from .forms import (
    CoachCreateForm,
    SiteStatForm,
)


def can_access_coaches(user):

    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(
                name="مربیان"
            ).exists()
        )
    )


def is_manager(user):

    return (
        user.is_authenticated
        and user.is_superuser
    )


def coach_login(request):

    if can_access_coaches(request.user):

        return redirect(
            "coaches:dashboard"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:

            return render(
                request,
                "coaches/login.html",
                {
                    "error":
                        "نام کاربری یا رمز عبور اشتباه است."
                }
            )

        if not (
            user.is_superuser
            or user.groups.filter(
                name="مربیان"
            ).exists()
        ):

            return render(
                request,
                "coaches/login.html",
                {
                    "error":
                        "این حساب اجازه ورود به پنل مربیان را ندارد."
                }
            )

        login(
            request,
            user
        )

        return redirect(
            "coaches:dashboard"
        )

    return render(
        request,
        "coaches/login.html"
    )


@user_passes_test(
    can_access_coaches,
    login_url="/coaches/login/"
)
def dashboard(request):

    return render(
        request,
        "coaches/dashboard.html"
    )


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def coach_management(request):

    coaches = User.objects.filter(
        groups__name="مربیان"
    ).order_by(
        "first_name",
        "last_name"
    )

    return render(
        request,
        "coaches/coach_management.html",
        {
            "coaches": coaches
        }
    )


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def coach_create(request):

    if request.method == "POST":

        form = CoachCreateForm(
            request.POST
        )

        if form.is_valid():

            coach = form.save()

            coaches_group, created = (
                Group.objects.get_or_create(
                    name="مربیان"
                )
            )

            coach.groups.add(
                coaches_group
            )

            return redirect(
                "coaches:coach_management"
            )

    else:

        form = CoachCreateForm()

    return render(
        request,
        "coaches/coach_create.html",
        {
            "form": form
        }
    )


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def coach_delete(request, user_id):

    if request.method != "POST":

        return redirect(
            "coaches:coach_management"
        )

    coach = get_object_or_404(
        User,
        id=user_id
    )

    # مدیر اصلی حذف نمی‌شود
    if coach.is_superuser:

        return redirect(
            "coaches:coach_management"
        )

    # فقط اعضای گروه مربیان قابل حذف هستند
    if not coach.groups.filter(
        name="مربیان"
    ).exists():

        return redirect(
            "coaches:coach_management"
        )

    coach.delete()

    return redirect(
        "coaches:coach_management"
    )


def coach_logout(request):

    logout(request)

    return redirect(
        "coaches:login"
    )


# =========================================================
# SITE STATS
# =========================================================


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def site_stats(request):

    stats = SiteStat.objects.all().order_by(
        "order"
    )

    return render(
        request,
        "coaches/site_stats.html",
        {
            "stats": stats
        }
    )


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def site_stat_create(request):

    if request.method == "POST":

        form = SiteStatForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "coaches:site_stats"
            )

    else:

        form = SiteStatForm()

    return render(
        request,
        "coaches/site_stat_form.html",
        {
            "form": form,
            "page_title": "افزودن آمار"
        }
    )


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def site_stat_edit(request, stat_id):

    stat = get_object_or_404(
        SiteStat,
        id=stat_id
    )

    if request.method == "POST":

        form = SiteStatForm(
            request.POST,
            instance=stat
        )

        if form.is_valid():

            form.save()

            return redirect(
                "coaches:site_stats"
            )

    else:

        form = SiteStatForm(
            instance=stat
        )

    return render(
        request,
        "coaches/site_stat_form.html",
        {
            "form": form,
            "page_title": "ویرایش آمار"
        }
    )


@user_passes_test(
    is_manager,
    login_url="/coaches/login/"
)
def site_stat_delete(request, stat_id):

    if request.method != "POST":

        return redirect(
            "coaches:site_stats"
        )

    stat = get_object_or_404(
        SiteStat,
        id=stat_id
    )

    stat.delete()

    return redirect(
        "coaches:site_stats"
    )