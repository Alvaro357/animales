"""
Script de prueba para el sistema de seguridad del login de admin

Este script prueba automáticamente las funcionalidades de:
- Límite de intentos fallidos
- Bloqueo temporal
- Mensajes de advertencia
- Reset después de login exitoso
- Expiración de bloqueos

Uso:
    python test_admin_login_security.py
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
import time


class AdminLoginSecurityTest(TestCase):
    """Tests para el sistema de seguridad del login de administración"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        self.login_url = reverse('admin_login')
        self.correct_password = settings.ADMIN_PASSWORD
        self.wrong_password = 'contraseña_incorrecta'

    def test_successful_login_first_attempt(self):
        """Test: Login exitoso en el primer intento"""
        response = self.client.post(self.login_url, {
            'password': self.correct_password
        })

        # Debe redirigir al panel de administración
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/panel/', response.url)

        # Verificar que la sesión está configurada
        session = self.client.session
        self.assertTrue(session.get('admin_authenticated'))

    def test_first_failed_attempt_shows_warning(self):
        """Test: Primer intento fallido muestra advertencia de 2 intentos restantes"""
        response = self.client.post(self.login_url, {
            'password': self.wrong_password
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contraseña incorrecta')
        self.assertContains(response, 'Te quedan 2 intentos')

    def test_second_failed_attempt_shows_warning(self):
        """Test: Segundo intento fallido muestra advertencia de 1 intento restante"""
        # Primer intento fallido
        self.client.post(self.login_url, {'password': self.wrong_password})

        # Segundo intento fallido
        response = self.client.post(self.login_url, {
            'password': self.wrong_password
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contraseña incorrecta')
        self.assertContains(response, 'Te queda 1 intento')

    def test_three_failed_attempts_blocks_access(self):
        """Test: Tres intentos fallidos bloquean el acceso"""
        # Tres intentos fallidos
        for _ in range(3):
            response = self.client.post(self.login_url, {
                'password': self.wrong_password
            })

        # El tercer intento debe mostrar bloqueo
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Has excedido el número máximo de intentos')
        self.assertContains(response, 'bloqueado por 15 minutos')

    def test_blocked_user_cannot_login_even_with_correct_password(self):
        """Test: Usuario bloqueado no puede hacer login ni con contraseña correcta"""
        # Bloquear con 3 intentos fallidos
        for _ in range(3):
            self.client.post(self.login_url, {'password': self.wrong_password})

        # Intentar con contraseña correcta
        response = self.client.post(self.login_url, {
            'password': self.correct_password
        })

        # Debe seguir mostrando bloqueo
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bloqueado temporalmente')

    def test_successful_login_resets_attempts(self):
        """Test: Login exitoso resetea el contador de intentos"""
        # Un intento fallido
        self.client.post(self.login_url, {'password': self.wrong_password})

        # Login exitoso
        response = self.client.post(self.login_url, {
            'password': self.correct_password
        })

        # Debe redirigir exitosamente
        self.assertEqual(response.status_code, 302)

        # Logout
        self.client.get(reverse('admin_logout'))

        # Nuevo intento fallido no debe mostrar "Te queda 1 intento"
        # sino "Te quedan 2 intentos" (contador reseteado)
        response = self.client.post(self.login_url, {
            'password': self.wrong_password
        })

        self.assertContains(response, 'Te quedan 2 intentos')

    def test_blocked_state_shows_disabled_form(self):
        """Test: Estado bloqueado muestra formulario deshabilitado"""
        # Bloquear con 3 intentos fallidos
        for _ in range(3):
            self.client.post(self.login_url, {'password': self.wrong_password})

        # Obtener la página de login
        response = self.client.get(self.login_url)

        # Verificar que el template recibe is_blocked=True
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_blocked'])
        self.assertIsNotNone(response.context['minutes_remaining'])

    def test_get_request_shows_login_form(self):
        """Test: Petición GET muestra el formulario de login normalmente"""
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Panel de Administración')
        self.assertContains(response, 'Contraseña')

    def test_different_sessions_tracked_separately(self):
        """Test: Sesiones diferentes son rastreadas por separado"""
        client1 = Client()
        client2 = Client()

        # Client1 falla 2 intentos
        for _ in range(2):
            client1.post(self.login_url, {'password': self.wrong_password})

        # Client2 debe tener intentos independientes
        response = client2.post(self.login_url, {
            'password': self.wrong_password
        })

        # Client2 debe mostrar "Te quedan 2 intentos" (no afectado por client1)
        # Nota: Este test asume que las IPs son diferentes o que el rastreo
        # considera la sesión además de la IP
        self.assertContains(response, 'Te quedan 2 intentos')


def run_manual_tests():
    """
    Función para ejecutar pruebas manuales interactivas
    Útil para verificación visual del comportamiento
    """
    print("\n" + "="*70)
    print("PRUEBAS MANUALES DEL SISTEMA DE SEGURIDAD - LOGIN ADMIN")
    print("="*70 + "\n")

    print("Para probar el sistema manualmente:")
    print("\n1. Ejecutar el servidor de desarrollo:")
    print("   python manage.py runserver\n")

    print("2. Navegar a: http://localhost:8000/admin/login/\n")

    print("3. CASO 1: Verificar mensajes de advertencia")
    print("   - Intentar contraseña incorrecta 1 vez")
    print("   - Verificar mensaje: 'Te quedan 2 intentos'")
    print("   - Intentar contraseña incorrecta otra vez")
    print("   - Verificar mensaje: 'Te queda 1 intento'\n")

    print("4. CASO 2: Verificar bloqueo")
    print("   - Intentar contraseña incorrecta por tercera vez")
    print("   - Verificar que aparece:")
    print("     * Mensaje de bloqueo por 15 minutos")
    print("     * Formulario deshabilitado")
    print("     * Contador visual de tiempo")
    print("     * Efecto de pulsación roja en el card\n")

    print("5. CASO 3: Verificar reset con login exitoso")
    print("   - Abrir navegador en modo incógnito o limpiar sesión")
    print("   - Fallar 1 intento")
    print("   - Ingresar contraseña correcta")
    print("   - Hacer logout")
    print("   - Fallar 1 intento nuevamente")
    print("   - Verificar que dice 'Te quedan 2 intentos' (reseteado)\n")

    print("6. CASO 4: Verificar expiración de bloqueo")
    print("   - Modificar BLOCK_DURATION_MINUTES a 1 en views.py")
    print("   - Provocar bloqueo con 3 intentos fallidos")
    print("   - Esperar 1 minuto")
    print("   - Recargar página o esperar auto-refresh")
    print("   - Verificar que el formulario se habilita\n")

    print("NOTAS DE SEGURIDAD:")
    print("- El rastreo es por dirección IP")
    print("- Los datos se almacenan en sesión de Django")
    print("- El bloqueo expira automáticamente después de 15 minutos")
    print("- Login exitoso limpia todos los intentos fallidos")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    print("\nEste script debe ejecutarse con Django:")
    print("python manage.py test test_admin_login_security\n")
    print("O para ver las instrucciones de pruebas manuales:\n")
    run_manual_tests()
