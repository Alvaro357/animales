# models.py - Versión corregida para migración segura

from django.db import models
from django.contrib.auth.models import User
import secrets
import hashlib
from django.utils import timezone
from .validators import validate_image_file, validate_video_file, validate_logo_file

class RegistroAsociacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=130)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200)
    poblacion = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    logo = models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True,
        validators=[validate_logo_file],
        help_text="Logo de la asociación (máximo 2MB, formatos: JPG, PNG)"
    )
    
    # ESTADOS ACTUALIZADOS para incluir pendiente y rechazada
    ESTADOS = [
        ('pendiente', 'Pendiente de Aprobación'),
        ('activa', 'Activa'),
        ('suspendida', 'Suspendida'),
        ('rechazada', 'Rechazada'),
        ('eliminada', 'Eliminada'),
    ]
    
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='pendiente',  # CAMBIO: Ahora por defecto es pendiente
        help_text="Estado actual de la asociación"
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True, 
        null=True, 
        blank=True,
        help_text="Fecha de registro de la asociación"
    )
    
    # CAMPO PROBLEMÁTICO - Ahora permite NULL y tiene default
    fecha_modificacion_estado = models.DateTimeField(
        auto_now=True, 
        null=True, 
        blank=True  # Permite NULL para migración segura
    )
    
    # NUEVOS CAMPOS PARA SISTEMA DE APROBACIÓN - Todos permiten NULL
    fecha_aprobacion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha cuando fue aprobada la asociación"
    )
    fecha_rechazo = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha cuando fue rechazada la asociación"
    )
    aprobada_por = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Quien aprobó la asociación"
    )
    notas_admin = models.TextField(
        blank=True, 
        null=True,
        help_text="Notas internas del administrador"
    )
    motivo_rechazo = models.TextField(
        blank=True, 
        null=True,
        help_text="Motivo del rechazo (visible para la asociación)"
    )
    
    # TOKENS DE GESTIÓN - Permiten blank para datos existentes
    token_gestion = models.CharField(
        max_length=64, 
        unique=True, 
        blank=True,
        help_text="Token único para gestión administrativa"
    )
    token_aprobacion = models.CharField(
        max_length=64, 
        unique=True, 
        blank=True,
        help_text="Token único para aprobación rápida"
    )
    
    # NUEVOS CAMPOS INFORMATIVOS
    datos_completos_enviados = models.BooleanField(
        default=False,
        help_text="Si ya se enviaron los datos completos al admin"
    )

    # CAMPOS PARA RESTABLECIMIENTO DE CONTRASEÑA
    token_reset_password = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Token único para restablecer contraseña"
    )
    token_reset_expira = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha de expiración del token de reset"
    )
    
    def save(self, *args, **kwargs):
        # Generar tokens si no existen
        if not self.token_gestion:
            self.token_gestion = self.generar_token_seguro('gestion')
        if not self.token_aprobacion:
            self.token_aprobacion = self.generar_token_seguro('aprobacion')
        
        # Si fecha_registro es null, usar fecha actual
        if not self.fecha_registro:
            self.fecha_registro = timezone.now()
            
        # Asegurar que fecha_modificacion_estado tenga un valor
        if not self.fecha_modificacion_estado:
            self.fecha_modificacion_estado = timezone.now()
            
        super().save(*args, **kwargs)
    
    def generar_token_seguro(self, tipo='gestion'):
        """Genera un token seguro único para gestión administrativa"""
        import time
        attempts = 0
        while attempts < 10:
            timestamp = str(int(time.time() * 1000000))
            base_string = f"{self.nombre}-{self.email}-{tipo}-{timestamp}-{secrets.token_hex(16)}"
            token = hashlib.sha256(base_string.encode()).hexdigest()
            
            # Verificar que sea único según el tipo
            if tipo == 'aprobacion':
                if not RegistroAsociacion.objects.filter(token_aprobacion=token).exists():
                    return token
            else:
                if not RegistroAsociacion.objects.filter(token_gestion=token).exists():
                    return token
            
            attempts += 1
            time.sleep(0.001)
            
        # Fallback si falla
        return hashlib.sha256(f"{self.nombre}-{self.email}-{tipo}-{secrets.token_hex(32)}".encode()).hexdigest()
    
    def puede_acceder(self):
        """Verifica si la asociación puede acceder al sistema"""
        return self.estado == 'activa'
    
    def esta_pendiente(self):
        """Verifica si está pendiente de aprobación"""
        return self.estado == 'pendiente'
    
    def esta_rechazada(self):
        """Verifica si fue rechazada"""
        return self.estado == 'rechazada'
    
    def aprobar(self, admin_name="Sistema", notas=""):
        """Aprueba la asociación"""
        self.estado = 'activa'
        self.fecha_aprobacion = timezone.now()
        self.aprobada_por = admin_name
        if notas:
            self.notas_admin = notas
        self.save()
    
    def rechazar(self, motivo="", admin_name="Sistema"):
        """Rechaza la asociación"""
        self.estado = 'rechazada'
        self.fecha_rechazo = timezone.now()
        self.motivo_rechazo = motivo
        self.aprobada_por = admin_name
        self.save()
    
    def get_estado_color(self):
        """Devuelve el color asociado al estado para la UI"""
        colores = {
            'pendiente': '#f59e0b',
            'activa': '#10b981',
            'suspendida': '#f59e0b',
            'rechazada': '#ef4444',
            'eliminada': '#6b7280',
        }
        return colores.get(self.estado, '#6b7280')
    
    def get_tiempo_desde_registro(self):
        """Calcula el tiempo transcurrido desde el registro"""
        if self.fecha_registro:
            delta = timezone.now() - self.fecha_registro
            if delta.days > 0:
                return f"Hace {delta.days} días"
            elif delta.seconds > 3600:
                horas = delta.seconds // 3600
                return f"Hace {horas} horas"
            else:
                minutos = delta.seconds // 60
                return f"Hace {minutos} minutos"
        return "Tiempo desconocido"

    def generar_token_reset_password(self):
        """Genera un token seguro para restablecer contraseña (válido 1 hora)"""
        import time
        timestamp = str(int(time.time() * 1000000))
        base_string = f"{self.nombre}-reset-{timestamp}-{secrets.token_hex(16)}"
        token = hashlib.sha256(base_string.encode()).hexdigest()

        self.token_reset_password = token
        self.token_reset_expira = timezone.now() + timezone.timedelta(hours=1)
        self.save(update_fields=['token_reset_password', 'token_reset_expira'])
        return token

    def validar_token_reset(self, token):
        """Valida si el token de reset es válido y no ha expirado"""
        if not self.token_reset_password or not self.token_reset_expira:
            return False
        if self.token_reset_password != token:
            return False
        if timezone.now() > self.token_reset_expira:
            return False
        return True

    def limpiar_token_reset(self):
        """Limpia el token de reset después de usarlo"""
        self.token_reset_password = None
        self.token_reset_expira = None
        self.save(update_fields=['token_reset_password', 'token_reset_expira'])

    class Meta:
        db_table = 'asociaciones'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"

# Los demás modelos permanecen igual
class CreacionAnimales(models.Model):
    asociacion = models.ForeignKey(RegistroAsociacion, on_delete=models.CASCADE, related_name='animales')
    nombre = models.CharField(max_length=100)
    tipo_de_animal = models.CharField(max_length=200)
    raza = models.CharField(max_length=50)
    imagen = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL de la foto del animal en Backblaze B2"
    )
    video = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL del video del animal en Backblaze B2"
    )
    email = models.EmailField()
    telefono = models.CharField(max_length=130)
    poblacion = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    adoptado = models.BooleanField(default=False)
    color = models.CharField(
        max_length=100,
        help_text="Color del animal (ej: marrón, negro, blanco, manchado, etc.)",
        blank=False,
        null=False,
        default="No especificado"
    )

    TAMANOS = [
        ('Mini', 'Mini'),
        ('Pequeño', 'Pequeño'),
        ('Mediano-Pequeño', 'Mediano-Pequeño'),
        ('Mediano', 'Mediano'),
        ('Mediano-Grande', 'Mediano-Grande'),
        ('Grande', 'Grande'),
    ]

    tamano = models.CharField(
        max_length=20,
        choices=TAMANOS,
        help_text="Tamaño del animal",
        blank=False,
        null=False,
        default="Mediano"
    )

    class Meta:
        db_table = 'Animales'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    def get_primera_imagen(self):
        """Retorna la URL de la primera imagen (nueva o legacy)"""
        # Primero buscar la imagen marcada como principal
        primera_imagen = self.imagenes.filter(es_principal=True).first()
        if primera_imagen:
            return primera_imagen.imagen
        # Si no hay principal, buscar la primera imagen por orden
        primera_cualquiera = self.imagenes.first()
        if primera_cualquiera:
            return primera_cualquiera.imagen
        # Fallback al campo legacy
        return self.imagen if self.imagen else None

class AnimalFavorito(models.Model):
    usuario_ip = models.GenericIPAddressField()
    asociacion = models.ForeignKey(RegistroAsociacion, on_delete=models.CASCADE, null=True, blank=True)
    animal = models.ForeignKey(CreacionAnimales, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario_ip', 'animal']

class ImagenAnimal(models.Model):
    """Modelo para almacenar múltiples imágenes de un animal"""
    animal = models.ForeignKey(CreacionAnimales, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.URLField(
        max_length=500,
        help_text="URL de la imagen del animal en Cloudinary"
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de visualización de la imagen"
    )
    es_principal = models.BooleanField(
        default=False,
        help_text="Indica si es la imagen principal del animal"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'imagenes_animales'
        ordering = ['orden', '-es_principal', '-fecha_subida']
        verbose_name = 'Imagen de Animal'
        verbose_name_plural = 'Imágenes de Animales'

    def __str__(self):
        return f"Imagen de {self.animal.nombre} - Orden {self.orden}"

    def save(self, *args, **kwargs):
        # Si se marca como principal, desmarcar las demás
        if self.es_principal:
            ImagenAnimal.objects.filter(animal=self.animal, es_principal=True).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)

class VideoAnimal(models.Model):
    """Modelo para almacenar múltiples videos de un animal"""
    animal = models.ForeignKey(CreacionAnimales, on_delete=models.CASCADE, related_name='videos')
    video = models.URLField(
        max_length=500,
        help_text="URL del video del animal en Cloudinary"
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de visualización del video"
    )
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Descripción opcional del video"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'videos_animales'
        ordering = ['orden', '-fecha_subida']
        verbose_name = 'Video de Animal'
        verbose_name_plural = 'Videos de Animales'

    def __str__(self):
        return f"Video de {self.animal.nombre} - Orden {self.orden}"