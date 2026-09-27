from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="auth-home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("resident/dashboard/", views.resident_dashboard_view, name="resident-dashboard"),
    path("staff/dashboard/", views.admin_dashboard_view, name="admin-dashboard"),
    path("register/", views.resident_register_view, name="register"),
    path("login/", views.resident_login_view, name="login"),
    path("staff/login/", views.admin_login_view, name="admin-login"),
    path("staff/register/", views.admin_register_view, name="admin-register"),
    path("logout/", views.logout_view, name="logout"),
    path("complaints/", views.complaint_list_view, name="complaint-list"),
    path("complaints/new/", views.complaint_create_view, name="complaint-create"),
    path("complaints/<int:pk>/update/", views.complaint_update_view, name="complaint-update"),
    path("complaints/<int:pk>/delete/", views.complaint_delete_view, name="complaint-delete"),
    path("staff/complaints/", views.complaint_list_view, name="admin-complaints"),
    path("staff/notices/", views.notice_list_view, name="admin-notices"),
    path("staff/notices/<int:pk>/edit/", views.notice_update_view, name="notice-update"),
    path("staff/notices/<int:pk>/delete/", views.notice_delete_view, name="notice-delete"),
]