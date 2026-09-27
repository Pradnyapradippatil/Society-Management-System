from django.apps import AppConfig


class SocietyConfig(AppConfig):
    name = "society"

    def ready(self):
        from . import signals  # noqa: F401
