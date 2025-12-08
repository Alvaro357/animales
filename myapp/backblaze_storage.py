import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import uuid
import os


class BackblazeStorage:
    """
    Clase para gestionar la subida de archivos a Backblaze B2 usando S3 API.
    """

    def __init__(self):
        """Inicializa el cliente S3 para Backblaze."""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{settings.BACKBLAZE_ENDPOINT}',
            aws_access_key_id=settings.BACKBLAZE_KEY_ID,
            aws_secret_access_key=settings.BACKBLAZE_APPLICATION_KEY,
            region_name=settings.BACKBLAZE_REGION
        )
        self.bucket_name = settings.BACKBLAZE_BUCKET_NAME

    def upload_file(self, file_obj, folder='Fotos', file_name=None):
        """
        Sube un archivo a Backblaze B2.

        Args:
            file_obj: Objeto de archivo de Django (UploadedFile)
            folder: Carpeta en el bucket ('Fotos' o 'videos')
            file_name: Nombre del archivo (opcional, se genera automáticamente si no se proporciona)

        Returns:
            str: URL pública del archivo subido o None si hay error
        """
        try:
            # Generar nombre único si no se proporciona
            if not file_name:
                ext = os.path.splitext(file_obj.name)[1]
                file_name = f"{uuid.uuid4()}{ext}"

            # Crear la clave (key) completa con la carpeta
            key = f"{folder}/{file_name}"

            # Determinar el content type
            content_type = file_obj.content_type if hasattr(file_obj, 'content_type') else 'application/octet-stream'

            # Subir el archivo
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'max-age=31536000',  # Cache por 1 año
                }
            )

            # Construir la URL pública
            public_url = f"https://{self.bucket_name}.{settings.BACKBLAZE_ENDPOINT}/{key}"

            return public_url

        except ClientError as e:
            print(f"Error al subir archivo a Backblaze: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al subir archivo: {e}")
            return None

    def delete_file(self, file_url):
        """
        Elimina un archivo de Backblaze B2.

        Args:
            file_url: URL completa del archivo a eliminar

        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Extraer la clave (key) de la URL
            # Ejemplo: https://asociacionanimales.s3.eu-central-003.backblazeb2.com/Fotos/imagen.jpg
            # Extraemos: Fotos/imagen.jpg
            parts = file_url.split(f"{self.bucket_name}.{settings.BACKBLAZE_ENDPOINT}/")
            if len(parts) < 2:
                print(f"URL no válida: {file_url}")
                return False

            key = parts[1]

            # Eliminar el archivo
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

            return True

        except ClientError as e:
            print(f"Error al eliminar archivo de Backblaze: {e}")
            return False
        except Exception as e:
            print(f"Error inesperado al eliminar archivo: {e}")
            return False

    def upload_image(self, image_file, file_name=None):
        """
        Sube una imagen a la carpeta Fotos.

        Args:
            image_file: Archivo de imagen
            file_name: Nombre del archivo (opcional)

        Returns:
            str: URL pública de la imagen subida
        """
        return self.upload_file(image_file, folder='Fotos', file_name=file_name)

    def upload_video(self, video_file, file_name=None):
        """
        Sube un video a la carpeta videos.

        Args:
            video_file: Archivo de video
            file_name: Nombre del archivo (opcional)

        Returns:
            str: URL pública del video subido
        """
        return self.upload_file(video_file, folder='videos', file_name=file_name)


# Instancia global para uso en views
backblaze_storage = BackblazeStorage()
