from django.urls import path

from . import views


app_name = "coaches"


urlpatterns = [

    # =====================================================
    # DASHBOARD
    # =====================================================

    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "login/",
        views.coach_login,
        name="login"
    ),

    path(
        "logout/",
        views.coach_logout,
        name="logout"
    ),


    # =====================================================
    # COACH MANAGEMENT
    # =====================================================

    path(
        "management/",
        views.coach_management,
        name="coach_management"
    ),

    path(
        "management/coaches/add/",
        views.coach_create,
        name="coach_create"
    ),

    path(
        "management/coaches/<int:user_id>/delete/",
        views.coach_delete,
        name="coach_delete"
    ),


    # =====================================================
    # SITE STATS
    # =====================================================

    path(
        "site-stats/",
        views.site_stats,
        name="site_stats"
    ),

    path(
        "site-stats/create/",
        views.site_stat_create,
        name="site_stat_create"
    ),

    path(
        "site-stats/<int:stat_id>/edit/",
        views.site_stat_edit,
        name="site_stat_edit"
    ),

    path(
        "site-stats/<int:stat_id>/delete/",
        views.site_stat_delete,
        name="site_stat_delete"
    ),
]