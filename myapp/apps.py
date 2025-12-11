from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        """
        Importa y registra los signals cuando la aplicación está lista.

        Este método se ejecuta una vez al iniciar Django y registra
        automáticamente todos los signals definidos en signals.py
        """
        import myapp.signals  # noqa: F401
