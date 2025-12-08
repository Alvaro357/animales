"""
Script para probar la conexión y subida a Cloudinary
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.cloudinary_storage import cloudinary_storage
import io

def test_cloudinary_connection():
    """Prueba la conexión a Cloudinary"""
    print("Probando conexion a Cloudinary...\n")
    print("Cloud name: dfg7cdvlo")
    print("API Key: 884186126363959\n")

    try:
        # Crear un archivo de prueba
        print("Subiendo imagen de prueba...")
        test_content = b"Test image from Django - Asociaciones de Animales"
        test_file = io.BytesIO(test_content)
        test_file.name = "test.txt"
        test_file.content_type = "text/plain"

        # Subir archivo de prueba como raw (no es una imagen real)
        url = cloudinary_storage.upload_file(test_file, folder='animales/fotos', resource_type='raw')

        if url:
            print("OK - Archivo subido exitosamente a Cloudinary!")
            print(f"\nURL generada: {url}")
            print("\n" + "="*70)
            print("PRUEBA FINAL:")
            print("="*70)
            print("\n1. Abre esta URL en tu navegador:")
            print(f"   {url}")
            print("\n2. Deberias ver el archivo de prueba.")
            print("\n3. Las imagenes de animales ahora se subiran a Cloudinary")
            print("   y se veran automaticamente en la web!")
            print("\n4. Ventajas de Cloudinary:")
            print("   - 25 GB almacenamiento GRATIS")
            print("   - 25 GB ancho de banda mensual GRATIS")
            print("   - CDN global (carga rapida en todo el mundo)")
            print("   - Optimizacion automatica de imagenes")
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
        print("   2. Problema de conexion a internet")
        print("   3. API Key sin permisos")

if __name__ == "__main__":
    test_cloudinary_connection()
