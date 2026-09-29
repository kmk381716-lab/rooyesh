from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render


User = get_user_model()

LIBRARY_ADMIN_GROUP = "ادمین کتابخانه"


def is_main_admin(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_main_admin, login_url="/coaches/login/")
def library(request):
    return render(request, "library/index.html")


@user_passes_test(is_main_admin, login_url="/coaches/login/")
def library_dashboard(request):
    return render(request, "library/dashboard/index.html")


@user_passes_test(is_main_admin, login_url="/coaches/login/")
def library_admin_list(request):
    group, _ = Group.objects.get_or_create(
        name=LIBRARY_ADMIN_GROUP
    )

    library_admins = User.objects.filter(
        groups=group
    ).order_by("username")

    return render(
        request,
        "library/dashboard/admins.html",
        {
            "library_admins": library_admins
        }
    )


@user_passes_test(is_main_admin, login_url="/coaches/login/")
def library_admin_create(request):

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            group, _ = Group.objects.get_or_create(
                name=LIBRARY_ADMIN_GROUP
            )

            user.groups.add(group)

            return redirect("library_admin_list")

    else:
        form = UserCreationForm()

    return render(
        request,
        "library/dashboard/admin_create.html",
        {
            "form": form
        }
    )


@user_passes_test(is_main_admin, login_url="/coaches/login/")
def library_admin_toggle(request, user_id):

    if request.method != "POST":
        return redirect("library_admin_list")

    group = get_object_or_404(
        Group,
        name=LIBRARY_ADMIN_GROUP
    )

    user = get_object_or_404(
        User,
        id=user_id,
        groups=group
    )

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    return redirect("library_admin_list")


@user_passes_test(is_main_admin, login_url="/coaches/login/")
def library_admin_delete(request, user_id):

    if request.method != "POST":
        return redirect("library_admin_list")

    group = get_object_or_404(
        Group,
        name=LIBRARY_ADMIN_GROUP
    )

    user = get_object_or_404(
        User,
        id=user_id,
        groups=group
    )

    user.delete()

    return redirect("library_admin_list")