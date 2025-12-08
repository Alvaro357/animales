"""
Script para probar la conexión y subida a Backblaze B2
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.backblaze_storage import backblaze_storage
import io

def test_backblaze_connection():
    """Prueba la conexión a Backblaze"""
    print("Probando conexion a Backblaze B2...\n")
    print(f"Bucket: asociacionanimales")
    print(f"Endpoint: s3.eu-central-003.backblazeb2.com\n")

    try:
        # Crear un archivo de prueba
        print("Subiendo archivo de prueba...")
        test_content = b"Test file from Django - Asociaciones de Animales"
        test_file = io.BytesIO(test_content)
        test_file.name = "test.txt"
        test_file.content_type = "text/plain"

        # Subir archivo de prueba
        url = backblaze_storage.upload_file(test_file, folder='Fotos', file_name='test-django.txt')

        if url:
            print("OK - Archivo subido exitosamente!")
            print(f"\nURL generada: {url}")
            print("\n" + "="*70)
            print("PRUEBA FINAL:")
            print("="*70)
            print("\n1. Abre esta URL en tu navegador:")
            print(f"   {url}")
            print("\n2. Que deberia pasar:")
            print("   - Si ves el texto 'Test file from Django', TODO FUNCIONA!")
            print("   - Si ves error 403 o 'Access Denied', el bucket NO es publico")
            print("\n3. Si no es publico, ve a Backblaze y:")
            print("   - Selecciona el bucket 'asociacionanimales'")
            print("   - En 'Bucket Settings', cambia 'Files in Bucket' a 'Public'")
            print("="*70)
        else:
            print("ERROR - No se pudo subir archivo")
            print("Revisa los logs arriba para mas detalles")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        print("\nDetalle completo del error:")
        traceback.print_exc()
        print("\nPosibles causas:")
        print("   1. Credenciales incorrectas")
        print("   2. El bucket 'asociacionanimales' no existe")
        print("   3. Las credenciales no tienen permisos de escritura")

if __name__ == "__main__":
    test_backblaze_connection()
