from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class SocietyUserManager(BaseUserManager):
	def create_user(self, email, full_name, password=None, **extra_fields):
		if not email:
			raise ValueError("The email field must be set")
		if not full_name:
			raise ValueError("The full name field must be set")
		email = self.normalize_email(email)
		user = self.model(email=email, full_name=full_name, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, full_name, password=None, **extra_fields):
		extra_fields.setdefault("role", SocietyUser.Role.ADMIN)
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("is_active", True)

		if extra_fields.get("is_staff") is not True:
			raise ValueError("Superuser must have is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Superuser must have is_superuser=True.")

		return self.create_user(email, full_name, password, **extra_fields)


class SocietyUser(AbstractBaseUser, PermissionsMixin):
	class Role(models.TextChoices):
		RESIDENT = "resident", "Resident"
		ADMIN = "admin", "Admin"

	full_name = models.CharField(max_length=150)
	email = models.EmailField(unique=True)
	flat_number = models.CharField(max_length=20, blank=True)
	phone = models.CharField(max_length=20, blank=True)
	role = models.CharField(max_length=20, choices=Role.choices, default=Role.RESIDENT)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	date_joined = models.DateTimeField(auto_now_add=True)

	objects = SocietyUserManager()

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["full_name"]

	def __str__(self):
		return self.full_name or self.email

	@property
	def is_admin_role(self):
		return self.role == self.Role.ADMIN


class Complaint(models.Model):
	class Category(models.TextChoices):
		WATER = "water", "Water"
		ELECTRICITY = "electricity", "Electricity"
		MAINTENANCE = "maintenance", "Maintenance"
		LIFT = "lift", "Lift"
		SECURITY = "security", "Security"
		CLEANING = "cleaning", "Cleaning"
		OTHER = "other", "Other"

	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		IN_PROGRESS = "in_progress", "In Progress"
		RESOLVED = "resolved", "Resolved"

	resident = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="complaints",
	)
	title = models.CharField(max_length=150)
	category = models.CharField(max_length=30, choices=Category.choices)
	description = models.TextField()
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.title} - {self.get_status_display()}"


class Notice(models.Model):
	title = models.CharField(max_length=150)
	description = models.TextField()
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="notices_created",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return self.title
