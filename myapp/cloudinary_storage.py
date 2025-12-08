import cloudinary
import cloudinary.uploader
from django.conf import settings
import uuid
import os


class CloudinaryStorage:
    """
    Clase para gestionar la subida de archivos a Cloudinary.
    """

    def __init__(self):
        """Inicializa la configuración de Cloudinary."""
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    def upload_file(self, file_obj, folder='animales', resource_type='image'):
        """
        Sube un archivo a Cloudinary.

        Args:
            file_obj: Objeto de archivo de Django (UploadedFile)
            folder: Carpeta en Cloudinary ('animales/fotos' o 'animales/videos')
            resource_type: Tipo de recurso ('image' o 'video')

        Returns:
            str: URL pública del archivo subido o None si hay error
        """
        try:
            # Generar un public_id único
            ext = os.path.splitext(file_obj.name)[1].lower()
            public_id = f"{folder}/{uuid.uuid4()}"

            # Subir el archivo a Cloudinary
            result = cloudinary.uploader.upload(
                file_obj,
                public_id=public_id,
                resource_type=resource_type,
                overwrite=True,
                invalidate=True
            )

            # Retornar la URL segura (HTTPS)
            return result.get('secure_url')

        except Exception as e:
            print(f"Error al subir archivo a Cloudinary: {e}")
            return None

    def delete_file(self, file_url):
        """
        Elimina un archivo de Cloudinary.

        Args:
            file_url: URL completa del archivo a eliminar

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Extraer el public_id de la URL
            # Ejemplo URL: https://res.cloudinary.com/dfg7cdvlo/image/upload/v1234567890/animales/fotos/uuid.jpg
            # Public ID: animales/fotos/uuid

            if 'cloudinary.com' not in file_url:
                return False

            # Extraer la parte después de /upload/
            parts = file_url.split('/upload/')
            if len(parts) < 2:
                return False

            # Obtener el path después de la versión (v1234567890/)
            path_with_version = parts[1]
            path_parts = path_with_version.split('/')

            # Saltar la versión si existe (empieza con 'v' seguido de números)
            if path_parts[0].startswith('v') and path_parts[0][1:].isdigit():
                path_parts = path_parts[1:]

            # Reconstruir el public_id sin la extensión
            public_id = '/'.join(path_parts)
            # Quitar la extensión del archivo
            public_id = os.path.splitext(public_id)[0]

            # Determinar el tipo de recurso
            resource_type = 'video' if 'videos' in public_id else 'image'

            # Eliminar el archivo
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)

            return result.get('result') == 'ok'

        except Exception as e:
            print(f"Error al eliminar archivo de Cloudinary: {e}")
            return False

    def upload_image(self, image_file):
        """
        Sube una imagen a la carpeta animales/fotos.

        Args:
            image_file: Archivo de imagen

        Returns:
            str: URL pública de la imagen subida
        """
        return self.upload_file(image_file, folder='animales/fotos', resource_type='image')

    def upload_video(self, video_file):
        """
        Sube un video a la carpeta animales/videos.

        Args:
            video_file: Archivo de video

        Returns:
            str: URL pública del video subido
        """
        return self.upload_file(video_file, folder='animales/videos', resource_type='video')


# Instancia global para uso en views
cloudinary_storage = CloudinaryStorage()
