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
    imagen = models.ImageField(
        upload_to='animales/fotos/',
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text="Foto del animal (máximo 5MB, formatos: JPG, PNG, GIF, WebP)"
    )
    video = models.FileField(
        upload_to='animales/videos/',
        blank=True,
        null=True,
        validators=[validate_video_file],
        help_text="Video del animal (máximo 10MB, formatos: MP4, AVI, MOV, WebM)"
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

    class Meta:
        db_table = 'Animales'
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return self.nombre

class AnimalFavorito(models.Model):
    usuario_ip = models.GenericIPAddressField()
    asociacion = models.ForeignKey(RegistroAsociacion, on_delete=models.CASCADE, null=True, blank=True)
    animal = models.ForeignKey(CreacionAnimales, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        unique_together = ['usuario_ip', 'animal']