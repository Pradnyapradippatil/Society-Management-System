from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name != "society":
        return

    user_model = get_user_model()
    user_model.objects.get_or_create(
        email="admin@society.com",
        defaults={
            "full_name": "Default Admin",
            "flat_number": "",
            "phone": "",
            "role": user_model.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )
    admin_user = user_model.objects.filter(email="admin@society.com").first()
    if admin_user and not admin_user.check_password("admin123"):
        admin_user.set_password("admin123")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.role = user_model.Role.ADMIN
        admin_user.save(update_fields=["password", "is_staff", "is_superuser", "role"])