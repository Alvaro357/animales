"""
Middleware para manejar ngrok y otros proxies, especialmente para webhooks de Telegram
"""
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class NgrokMiddleware(MiddlewareMixin):
    """
    Middleware mejorado para manejar correctamente las peticiones de ngrok y webhooks de Telegram
    """
    def process_request(self, request):
        # Logging para debugging del webhook
        if request.path == '/telegram/webhook/':
            logger.info(f"Webhook request detected: {request.method} {request.path}")
            logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
            logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")

        # Configuración específica para ngrok
        if 'ngrok' in request.META.get('HTTP_HOST', ''):
            # Headers necesarios para ngrok
            request.META['HTTP_X_FORWARDED_HOST'] = request.META.get('HTTP_HOST')
            request.META['HTTP_X_FORWARDED_PROTO'] = 'https'

            # Para webhooks de Telegram a través de ngrok
            if request.path == '/telegram/webhook/':
                request.META['HTTP_ACCEPT'] = 'application/json'
                # Asegurar que el Content-Type esté bien configurado
                if not request.META.get('CONTENT_TYPE'):
                    request.META['CONTENT_TYPE'] = 'application/json'

        # Configuración general para webhooks de Telegram (independiente de ngrok)
        if request.path == '/telegram/webhook/':
            # Asegurar headers necesarios para Telegram
            if not request.META.get('HTTP_ACCEPT'):
                request.META['HTTP_ACCEPT'] = 'application/json'

            # Log adicional para debugging
            logger.debug(f"Webhook headers after middleware: {dict(request.headers)}")

        return None

    def process_response(self, request, response):
        # Headers de respuesta para ngrok
        if 'ngrok' in request.META.get('HTTP_HOST', ''):
            response['X-Frame-Options'] = 'SAMEORIGIN'
            response['Content-Security-Policy'] = "frame-ancestors 'self' https://*.ngrok.io https://*.ngrok-free.app"

        # Headers específicos para webhooks de Telegram
        if request.path == '/telegram/webhook/':
            response['Content-Type'] = 'application/json'
            # Permitir requests de Telegram
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-Telegram-Bot-Api-Secret-Token'

            logger.info(f"Webhook response: {response.status_code}")

        return response