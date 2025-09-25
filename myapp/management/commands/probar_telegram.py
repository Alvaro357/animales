# myapp/management/commands/probar_telegram.py

from django.core.management.base import BaseCommand
from myapp.telegram_utils import probar_telegram, probar_botones_telegram, verificar_webhook_url

class Command(BaseCommand):
    help = 'Prueba el sistema de notificaciones de Telegram y botones interactivos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--botones',
            action='store_true',
            help='Probar los botones interactivos de Telegram',
        )
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Verificar la configuración del webhook',
        )
        parser.add_argument(
            '--todo',
            action='store_true',
            help='Ejecutar todas las pruebas',
        )

    def handle(self, *args, **options):
        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS("🤖 PRUEBAS DEL SISTEMA DE TELEGRAM"))
        self.stdout.write("="*60)

        if options['todo'] or not any([options['botones'], options['webhook']]):
            # Ejecutar todas las pruebas por defecto
            self.probar_configuracion_basica()
            self.probar_webhook()
            self.probar_sistema_botones()
        else:
            if options['webhook']:
                self.probar_webhook()
            if options['botones']:
                self.probar_sistema_botones()

        self.stdout.write("="*60)
        self.stdout.write(self.style.SUCCESS("✅ Pruebas completadas"))

    def probar_configuracion_basica(self):
        """Prueba la configuración básica de Telegram"""
        self.stdout.write("\n📡 Probando configuración básica de Telegram...")

        try:
            resultado = probar_telegram()
            if resultado:
                self.stdout.write(
                    self.style.SUCCESS("✅ Configuración básica funcionando correctamente")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Error en la configuración básica")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"💥 Error en prueba básica: {e}")
            )

    def probar_webhook(self):
        """Prueba la configuración del webhook"""
        self.stdout.write("\n🔗 Verificando configuración del webhook...")

        try:
            resultado = verificar_webhook_url()
            if resultado:
                self.stdout.write(
                    self.style.SUCCESS("✅ Webhook configurado correctamente")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("⚠️ Webhook no configurado o con problemas")
                )
                self.stdout.write("💡 Para configurar el webhook, usa:")
                self.stdout.write("   python manage.py configurar_webhook")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"💥 Error verificando webhook: {e}")
            )

    def probar_sistema_botones(self):
        """Prueba el sistema de botones interactivos"""
        self.stdout.write("\n🎮 Probando sistema de botones interactivos...")

        try:
            resultado = probar_botones_telegram()
            if resultado:
                self.stdout.write(
                    self.style.SUCCESS("✅ Mensaje con botones enviado exitosamente")
                )
                self.stdout.write("💡 Ve a Telegram y presiona los botones para probar el webhook")
                self.stdout.write("📊 Revisa los logs del servidor para ver los callbacks")
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Error enviando mensaje con botones")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"💥 Error en prueba de botones: {e}")
            )