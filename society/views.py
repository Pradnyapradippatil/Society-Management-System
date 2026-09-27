from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AdminRegistrationForm,
    ComplaintForm,
    ComplaintSearchForm,
    ComplaintStatusForm,
    EmailAuthenticationForm,
    NoticeForm,
    ResidentRegistrationForm,
)
from .models import Complaint, Notice, SocietyUser


def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.role == SocietyUser.Role.ADMIN)


def is_resident_user(user):
    return user.is_authenticated and user.role == SocietyUser.Role.RESIDENT


def home_view(request):
    return render(request, "society/auth_home.html")


def _redirect_post_login(user):
    return redirect("admin-dashboard" if user.is_staff or user.role == SocietyUser.Role.ADMIN else "dashboard")


def resident_register_view(request):
    if request.user.is_authenticated:
        return _redirect_post_login(request.user)
    form = ResidentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Resident account created successfully.")
        return redirect("dashboard")
    return render(request, "society/auth_form.html", {"form": form, "page_title": "Resident Registration", "submit_label": "Create resident account", "intro": "Register as a resident to raise complaints and view notices.", "back_url": "login"})


def resident_login_view(request):
    if request.user.is_authenticated:
        return _redirect_post_login(request.user)
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if user.role != SocietyUser.Role.RESIDENT and not user.is_superuser:
            form.add_error(None, "This account is not a resident account.")
        else:
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}.")
            return redirect("dashboard")
    return render(request, "society/auth_form.html", {"form": form, "page_title": "Resident Login", "submit_label": "Login as resident", "intro": "Use your resident email and password.", "back_url": "register"})


def admin_login_view(request):
    if request.user.is_authenticated and is_admin_user(request.user):
        return redirect("admin-dashboard")
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not is_admin_user(user):
            form.add_error(None, "Only admin accounts can access the admin portal.")
        else:
            login(request, user)
            messages.success(request, f"Admin access granted for {user.full_name}.")
            return redirect("admin-dashboard")
    return render(request, "society/auth_form.html", {"form": form, "page_title": "Admin Login", "submit_label": "Login as admin", "intro": "Admins use the dedicated portal to manage complaints and notices.", "back_url": "auth-home"})


def admin_register_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return render(
            request,
            "society/auth_form.html",
            {
                "form": None,
                "page_title": "Admin Registration",
                "submit_label": "Create admin account",
                "intro": "Admin accounts are created by the seeded superuser or another superuser account.",
                "back_url": "admin-login",
                "info_title": "Restricted access",
                "info_message": "Use the admin login page with admin@society.com / admin123 to access the admin panel.",
            },
        )

    form = AdminRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Admin account created for {user.email}.")
        return redirect("admin-dashboard")
    return render(request, "society/auth_form.html", {"form": form, "page_title": "Admin Registration", "submit_label": "Create admin account", "intro": "Create new admin accounts from the protected admin setup page.", "back_url": "admin-dashboard"})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("auth-home")


@login_required
def dashboard_view(request):
    if is_admin_user(request.user):
        return redirect("admin-dashboard")
    return redirect("resident-dashboard")


@login_required
@user_passes_test(is_resident_user)
def resident_dashboard_view(request):
    notices = Notice.objects.all()[:5]
    complaints = Complaint.objects.filter(resident=request.user)
    counts = complaints.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status=Complaint.Status.PENDING)),
        resolved=Count("id", filter=Q(status=Complaint.Status.RESOLVED)),
    )
    return render(request, "society/resident/dashboard.html", {"notices": notices, "complaints": complaints[:5], "counts": counts})


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard_view(request):
    complaints = Complaint.objects.select_related("resident").all()
    counts = complaints.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status=Complaint.Status.PENDING)),
        resolved=Count("id", filter=Q(status=Complaint.Status.RESOLVED)),
    )
    notice_form = NoticeForm()
    latest_notices = Notice.objects.all()[:5]
    return render(request, "society/admin/dashboard.html", {"complaints": complaints[:8], "counts": counts, "notice_form": notice_form, "latest_notices": latest_notices})


@login_required
def complaint_list_view(request):
    if is_admin_user(request.user):
        complaints = Complaint.objects.select_related("resident").all()
    else:
        complaints = Complaint.objects.filter(resident=request.user).select_related("resident")
    form = ComplaintSearchForm(request.GET or None)
    if form.is_valid():
        query = form.cleaned_data.get("query")
        status = form.cleaned_data.get("status")
        complaint_date = form.cleaned_data.get("date")
        if query:
            complaints = complaints.filter(
                Q(resident__full_name__icontains=query)
                | Q(title__icontains=query)
                | Q(category__icontains=query)
            )
        if status:
            complaints = complaints.filter(status=status)
        if complaint_date:
            complaints = complaints.filter(created_at__date=complaint_date)
    template = "society/admin/complaints.html" if is_admin_user(request.user) else "society/resident/complaints.html"
    return render(request, template, {"form": form, "complaints": complaints})


@login_required
@user_passes_test(is_resident_user)
def complaint_create_view(request):
    form = ComplaintForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        complaint = form.save(commit=False)
        complaint.resident = request.user
        complaint.status = Complaint.Status.PENDING
        complaint.save()
        messages.success(request, "Complaint submitted successfully.")
        return redirect("resident-dashboard")
    return render(request, "society/resident/complaint_form.html", {"form": form})


@login_required
@user_passes_test(is_admin_user)
def complaint_update_view(request, pk):
    complaint = get_object_or_404(Complaint.objects.select_related("resident"), pk=pk)
    form = ComplaintStatusForm(request.POST or None, instance=complaint)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Complaint status updated.")
        return redirect("admin-complaints")
    return render(request, "society/admin/complaint_update.html", {"form": form, "complaint": complaint})


@login_required
@user_passes_test(is_admin_user)
def complaint_delete_view(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == "POST":
        complaint.delete()
        messages.success(request, "Complaint deleted.")
        return redirect("admin-complaints")
    return redirect("admin-complaints")


@login_required
@user_passes_test(is_admin_user)
def notice_list_view(request):
    notices = Notice.objects.all()
    form = NoticeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        notice = form.save(commit=False)
        notice.created_by = request.user
        notice.save()
        messages.success(request, "Notice published.")
        return redirect("admin-notices")
    return render(request, "society/admin/notices.html", {"notices": notices, "form": form})


@login_required
@user_passes_test(is_admin_user)
def notice_update_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    form = NoticeForm(request.POST or None, instance=notice)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Notice updated.")
        return redirect("admin-notices")
    return render(request, "society/admin/notice_form.html", {"form": form, "notice": notice, "page_title": "Edit Notice"})


@login_required
@user_passes_test(is_admin_user)
def notice_delete_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice deleted.")
    return redirect("admin-notices")