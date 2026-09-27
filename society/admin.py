from django.contrib import admin

from .models import Complaint, Notice, SocietyUser

@admin.register(SocietyUser)
class SocietyUserAdmin(admin.ModelAdmin):
	list_display = ("full_name", "email", "flat_number", "phone", "role", "is_staff", "is_active")
	list_filter = ("role", "is_staff", "is_active")
	search_fields = ("full_name", "email", "flat_number", "phone")
	ordering = ("full_name",)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
	list_display = ("id", "resident", "category", "title", "status", "created_at")
	list_filter = ("category", "status", "created_at")
	search_fields = ("title", "description", "resident__full_name", "resident__email")
	ordering = ("-created_at",)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
	list_display = ("title", "created_by", "created_at")
	search_fields = ("title", "description")
	ordering = ("-created_at",)
