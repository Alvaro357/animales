"""
Comando de gestión Django para configurar y probar el webhook de Telegram
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from myapp.telegram_utils import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, enviar_mensaje_telegram

class Command(BaseCommand):
    help = 'Configura y prueba el webhook de Telegram'

    def add_arguments(self, parser):
        parser.add_argument(
            '--webhook-url',
            type=str,
            help='URL completa del webhook (ej: https://tu-url.ngrok.io/telegram/webhook/)'
        )
        parser.add_argument(
            '--verificar',
            action='store_true',
            help='Solo verificar el estado actual del webhook'
        )
        parser.add_argument(
            '--probar',
            action='store_true',
            help='Enviar mensaje de prueba con botones'
        )
        parser.add_argument(
            '--eliminar',
            action='store_true',
            help='Eliminar el webhook actual'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('CONFIGURADOR DE TELEGRAM BOT'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        if options['verificar']:
            self.verificar_webhook()
        elif options['eliminar']:
            self.eliminar_webhook()
        elif options['probar']:
            self.enviar_prueba()
        elif options['webhook_url']:
            self.configurar_webhook(options['webhook_url'])
        else:
            # Mostrar menú interactivo
            self.menu_interactivo()

    def verificar_webhook(self):
        """Verifica el estado actual del webhook"""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                webhook_info = data['result']
                self.stdout.write("\n=== ESTADO DEL WEBHOOK ===")
                self.stdout.write(f"URL: {webhook_info.get('url', 'No configurado')}")
                self.stdout.write(f"Actualizaciones pendientes: {webhook_info.get('pending_update_count', 0)}")

                if webhook_info.get('last_error_date'):
                    self.stdout.write(self.style.WARNING(
                        f"Ultimo error: {webhook_info.get('last_error_message', 'Sin detalles')}"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS("Sin errores recientes"))

                return webhook_info.get('url', '')
        return None

    def configurar_webhook(self, webhook_url):
        """Configura el webhook en Telegram"""
        # Asegurar que la URL termina correctamente
        if not webhook_url.endswith('/telegram/webhook/'):
            webhook_url = webhook_url.rstrip('/') + '/telegram/webhook/'

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

        params = {
            'url': webhook_url,
            'allowed_updates': ['message', 'callback_query', 'inline_query'],
            'drop_pending_updates': False
        }

        self.stdout.write(f"\nConfigurando webhook: {webhook_url}")
        response = requests.post(url, json=params)

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                self.stdout.write(self.style.SUCCESS("\nWebhook configurado exitosamente!"))
                self.verificar_webhook()

                # Enviar notificación a Telegram
                mensaje = f"""✅ <b>WEBHOOK CONFIGURADO</b>

URL: {webhook_url}
Estado: Activo y funcionando

Los botones de Telegram ya deberían funcionar correctamente.
"""
                enviar_mensaje_telegram(mensaje)
                return True
            else:
                self.stdout.write(self.style.ERROR(
                    f"Error configurando webhook: {data.get('description', 'Sin descripción')}"
                ))
        return False

    def eliminar_webhook(self):
        """Elimina el webhook actual"""
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
        response = requests.post(url)

        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                self.stdout.write(self.style.SUCCESS("Webhook eliminado"))
                return True
        return False

    def enviar_prueba(self):
        """Envía un mensaje de prueba con botones"""
        # Crear una asociación de prueba en memoria para la demo
        mensaje = """🧪 <b>PRUEBA DE BOTONES DE TELEGRAM</b>

<b>Asociación de prueba:</b> Protectora Demo
<b>Email:</b> demo@example.com
<b>Ubicación:</b> Madrid, España

Prueba los siguientes botones:"""

        botones = [
            [
                {"text": "✅ Aprobar", "callback_data": "test_aprobar_1"},
                {"text": "❌ Rechazar", "callback_data": "test_rechazar_1"}
            ],
            [
                {"text": "👁️ Más Detalles", "callback_data": "test_ver_1"}
            ]
        ]

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

        params = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': mensaje,
            'parse_mode': 'HTML',
            'reply_markup': {'inline_keyboard': botones}
        }

        response = requests.post(url, json=params)

        if response.status_code == 200 and response.json()['ok']:
            self.stdout.write(self.style.SUCCESS("\nMensaje de prueba enviado a Telegram"))
            self.stdout.write("Verifica los botones en tu chat de Telegram")
        else:
            self.stdout.write(self.style.ERROR("Error enviando mensaje de prueba"))

    def menu_interactivo(self):
        """Muestra información y opciones"""
        webhook_actual = self.verificar_webhook()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("\nOPCIONES DISPONIBLES:"))
        self.stdout.write("\n1. Para configurar webhook con ngrok:")
        self.stdout.write("   - Instala ngrok: https://ngrok.com/download")
        self.stdout.write("   - Ejecuta: ngrok http 8000")
        self.stdout.write("   - Luego ejecuta:")
        self.stdout.write(self.style.SUCCESS(
            "     python manage.py configurar_telegram --webhook-url https://TU-URL.ngrok.io"
        ))

        self.stdout.write("\n2. Para verificar el estado actual:")
        self.stdout.write(self.style.SUCCESS("   python manage.py configurar_telegram --verificar"))

        self.stdout.write("\n3. Para enviar mensaje de prueba:")
        self.stdout.write(self.style.SUCCESS("   python manage.py configurar_telegram --probar"))

        self.stdout.write("\n4. Para eliminar el webhook:")
        self.stdout.write(self.style.SUCCESS("   python manage.py configurar_telegram --eliminar"))

        if not webhook_actual:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.ERROR("\nIMPORTANTE: No hay webhook configurado"))
            self.stdout.write("Los botones de Telegram NO funcionarán hasta que configures el webhook")

        self.stdout.write("\n" + "=" * 60)