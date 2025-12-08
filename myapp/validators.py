"""
Validadores de seguridad para archivos subidos
"""
import os
import mimetypes
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile


def validate_image_file(value):
    """
    Valida que el archivo subido sea una imagen válida y segura
    """
    if not value:
        return

    # Verificar tamaño del archivo (máximo 5MB)
    max_size = 5 * 1024 * 1024  # 5MB en bytes
    if value.size > max_size:
        raise ValidationError(
            f'El archivo es demasiado grande. Tamaño máximo permitido: 5MB. '
            f'Tamaño actual: {value.size / (1024 * 1024):.1f}MB'
        )

    # Verificar tipo de contenido
    allowed_content_types = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp'
    ]

    # Obtener content_type - maneja tanto UploadedFile como FieldFile
    content_type = getattr(value, 'content_type', None)
    if not content_type:
        # Si no tiene content_type (FieldFile), inferir del nombre
        content_type, _ = mimetypes.guess_type(value.name)

    if content_type and content_type not in allowed_content_types:
        raise ValidationError(
            f'Tipo de archivo no permitido: {content_type}. '
            f'Tipos permitidos: JPEG, PNG, GIF, WebP'
        )

    # Verificar extensión del archivo
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f'Extensión de archivo no permitida: {ext}. '
            f'Extensiones permitidas: {", ".join(allowed_extensions)}'
        )

    # Verificar que el nombre del archivo no contenga caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', '%', '$', '#', '@', '!', '`', '~']
    filename = value.name

    for char in dangerous_chars:
        if char in filename:
            raise ValidationError(
                f'El nombre del archivo contiene caracteres no permitidos: {char}'
            )

    # Verificar longitud del nombre del archivo
    if len(filename) > 100:
        raise ValidationError('El nombre del archivo es demasiado largo (máximo 100 caracteres)')


def validate_video_file(value):
    """
    Valida que el archivo subido sea un video válido y seguro
    """
    if not value:
        return

    # Verificar tamaño del archivo (máximo 10MB para videos)
    max_size = 10 * 1024 * 1024  # 10MB en bytes
    if value.size > max_size:
        raise ValidationError(
            f'El archivo es demasiado grande. Tamaño máximo permitido: 10MB. '
            f'Tamaño actual: {value.size / (1024 * 1024):.1f}MB'
        )

    # Verificar tipo de contenido
    allowed_content_types = [
        'video/mp4',
        'video/mpeg',
        'video/quicktime',
        'video/x-msvideo',  # AVI
        'video/webm'
    ]

    # Obtener content_type - maneja tanto UploadedFile como FieldFile
    content_type = getattr(value, 'content_type', None)
    if not content_type:
        # Si no tiene content_type (FieldFile), inferir del nombre
        content_type, _ = mimetypes.guess_type(value.name)

    if content_type and content_type not in allowed_content_types:
        raise ValidationError(
            f'Tipo de archivo no permitido: {content_type}. '
            f'Tipos permitidos: MP4, MPEG, MOV, AVI, WebM'
        )

    # Verificar extensión del archivo
    allowed_extensions = ['.mp4', '.mpeg', '.mpg', '.mov', '.avi', '.webm']
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f'Extensión de archivo no permitida: {ext}. '
            f'Extensiones permitidas: {", ".join(allowed_extensions)}'
        )

    # Verificar que el nombre del archivo no contenga caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', '%', '$', '#', '@', '!', '`', '~']
    filename = value.name

    for char in dangerous_chars:
        if char in filename:
            raise ValidationError(
                f'El nombre del archivo contiene caracteres no permitidos: {char}'
            )

    # Verificar longitud del nombre del archivo
    if len(filename) > 100:
        raise ValidationError('El nombre del archivo es demasiado largo (máximo 100 caracteres)')


def validate_logo_file(value):
    """
    Valida que el logo subido sea una imagen válida y segura (más restrictivo)
    """
    if not value:
        return

    # Verificar tamaño del archivo (máximo 2MB para logos)
    max_size = 2 * 1024 * 1024  # 2MB en bytes
    if value.size > max_size:
        raise ValidationError(
            f'El logo es demasiado grande. Tamaño máximo permitido: 2MB. '
            f'Tamaño actual: {value.size / (1024 * 1024):.1f}MB'
        )

    # Solo permitir JPEG y PNG para logos
    allowed_content_types = [
        'image/jpeg',
        'image/jpg',
        'image/png'
    ]

    # Obtener content_type - maneja tanto UploadedFile como FieldFile
    content_type = getattr(value, 'content_type', None)
    if not content_type:
        # Si no tiene content_type (FieldFile), inferir del nombre
        content_type, _ = mimetypes.guess_type(value.name)

    if content_type and content_type not in allowed_content_types:
        raise ValidationError(
            f'Tipo de archivo no permitido para logo: {content_type}. '
            f'Solo se permiten: JPEG, PNG'
        )

    # Verificar extensión del archivo
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f'Extensión de archivo no permitida para logo: {ext}. '
            f'Solo se permiten: JPG, JPEG, PNG'
        )

    # Verificar que el nombre del archivo no contenga caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', '%', '$', '#', '@', '!', '`', '~']
    filename = value.name

    for char in dangerous_chars:
        if char in filename:
            raise ValidationError(
                f'El nombre del archivo contiene caracteres no permitidos: {char}'
            )

    # Verificar longitud del nombre del archivo
    if len(filename) > 100:
        raise ValidationError('El nombre del archivo es demasiado largo (máximo 100 caracteres)')


def sanitize_filename(filename):
    """
    Sanitiza el nombre del archivo para hacerlo seguro
    """
    # Reemplazar espacios por guiones bajos
    filename = filename.replace(' ', '_')

    # Remover caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', '%', '$', '#', '@', '!', '`', '~', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '')

    # Asegurar que no esté vacío
    if not filename or filename == '.':
        filename = 'archivo'

    return filename