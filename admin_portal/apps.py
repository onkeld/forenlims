from django.apps import AppConfig, apps


class AdminPortalConfig(AppConfig):
    name = 'admin_portal'
    verbose_name = 'Administration Portal'

    def ready(self) -> None:
        self.autodiscover_menus()

    def autodiscover_menus(self) -> None:
        for app_config in apps.get_app_configs():
            try:
                __import__(f"{app_config.name}.admin_menu")
            except ModuleNotFoundError:
                pass
