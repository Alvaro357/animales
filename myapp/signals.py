# -*- coding: utf-8 -*-
# myapp/signals.py
"""
Sistema de Signals para Invalidacion Automatica de Cache

Este modulo implementa signals de Django que invalidan automaticamente
el cache cuando se crean, modifican o eliminan animales.

IMPORTANTE: Solo se invalida cache para operaciones con animales,
NO para asociaciones (registro/edicion de asociaciones no afecta el cache).
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
import logging

from .models import CreacionAnimales, ImagenAnimal, VideoAnimal

logger = logging.getLogger(__name__)


# ==================== SIGNALS PARA CREACIONANIMALES ====================

@receiver(post_save, sender=CreacionAnimales)
def invalidar_cache_al_guardar_animal(sender, instance, created, **kwargs):
    """
    Invalida el cache cuando se crea o actualiza un animal.

    Se ejecuta automaticamente despues de:
    - Crear un nuevo animal
    - Editar datos de un animal existente
    - Cambiar estado de adopcion
    """
    if created:
        logger.info(f"Animal creado: {instance.nombre} (ID: {instance.id}) - Invalidando cache")
    else:
        logger.info(f"Animal actualizado: {instance.nombre} (ID: {instance.id}) - Invalidando cache")

    # Invalidar caches generales
    cache.delete('inicio_animales')  # Vista de inicio (legacy)
    cache.delete('inicio_animales_v2')  # Vista de inicio (diccionarios optimizados)
    cache.delete('buscador_animales')  # Buscador avanzado (legacy)
    cache.delete('buscador_animales_v2')  # Buscador avanzado (diccionarios optimizados)
    cache.delete('animales_count')  # Contador de animales

    # Invalidar cache especifico de este animal
    cache.delete(f'animal_{instance.id}')

    # Invalidar cache por provincia (para busquedas filtradas)
    if instance.provincia:
        cache.delete(f'animales_provincia_{instance.provincia}')

    # Invalidar cache por tipo de animal
    if instance.tipo_de_animal:
        cache.delete(f'animales_tipo_{instance.tipo_de_animal}')

    logger.debug(f"Cache invalidado correctamente para animal ID {instance.id}")


@receiver(post_delete, sender=CreacionAnimales)
def invalidar_cache_al_eliminar_animal(sender, instance, **kwargs):
    """
    Invalida el cache cuando se elimina un animal.

    Se ejecuta automaticamente despues de eliminar un animal.
    """
    logger.info(f"Animal eliminado: {instance.nombre} (ID: {instance.id}) - Invalidando cache")

    # Invalidar los mismos caches que al guardar
    cache.delete('inicio_animales')  # Vista de inicio (legacy)
    cache.delete('inicio_animales_v2')  # Vista de inicio (diccionarios optimizados)
    cache.delete('buscador_animales')  # Buscador avanzado (legacy)
    cache.delete('buscador_animales_v2')  # Buscador avanzado (diccionarios optimizados)
    cache.delete('animales_count')
    cache.delete(f'animal_{instance.id}')

    if instance.provincia:
        cache.delete(f'animales_provincia_{instance.provincia}')

    if instance.tipo_de_animal:
        cache.delete(f'animales_tipo_{instance.tipo_de_animal}')

    logger.debug(f"Cache invalidado correctamente tras eliminar animal ID {instance.id}")


# ==================== SIGNALS PARA IMAGENES DE ANIMALES ====================

@receiver([post_save, post_delete], sender=ImagenAnimal)
def invalidar_cache_al_cambiar_imagen(sender, instance, **kwargs):
    """
    Invalida el cache cuando se añade/elimina una imagen de un animal.

    Importante: Las imagenes afectan la vista del animal especifico.
    """
    logger.info(f"Imagen modificada para animal ID: {instance.animal.id} - Invalidando cache")

    # Solo invalidar cache del animal especifico
    cache.delete(f'animal_{instance.animal.id}')

    # Tambien invalidar listas generales (porque pueden mostrar la imagen principal)
    cache.delete('inicio_animales')  # Vista de inicio (legacy)
    cache.delete('inicio_animales_v2')  # Vista de inicio (diccionarios optimizados)
    cache.delete('buscador_animales')  # Buscador avanzado (legacy)
    cache.delete('buscador_animales_v2')  # Buscador avanzado (diccionarios optimizados)

    logger.debug(f"Cache invalidado para imagenes del animal ID {instance.animal.id}")


# ==================== SIGNALS PARA VIDEOS DE ANIMALES ====================

@receiver([post_save, post_delete], sender=VideoAnimal)
def invalidar_cache_al_cambiar_video(sender, instance, **kwargs):
    """
    Invalida el cache cuando se añade/elimina un video de un animal.

    Importante: Los videos afectan la vista del animal especifico y listas generales.
    """
    logger.info(f"Video modificado para animal ID: {instance.animal.id} - Invalidando cache")

    # Invalidar cache del animal especifico
    cache.delete(f'animal_{instance.animal.id}')

    # Tambien invalidar listas generales (consistencia con ImagenAnimal)
    cache.delete('inicio_animales')  # Vista de inicio (legacy)
    cache.delete('inicio_animales_v2')  # Vista de inicio (diccionarios optimizados)
    cache.delete('buscador_animales')  # Buscador avanzado (legacy)
    cache.delete('buscador_animales_v2')  # Buscador avanzado (diccionarios optimizados)

    logger.debug(f"Cache invalidado para videos del animal ID {instance.animal.id}")


# ==================== FUNCIONES AUXILIARES ====================

def limpiar_todo_el_cache():
    """
    Funcion de utilidad para limpiar todo el cache manualmente.

    Uso:
        from myapp.signals import limpiar_todo_el_cache
        limpiar_todo_el_cache()
    """
    cache.clear()
    logger.warning("TODO el cache ha sido limpiado manualmente")


def invalidar_cache_animales():
    """
    Invalida selectivamente solo el cache relacionado con animales.

    Util para mantenimiento o actualizaciones masivas.
    """
    cache.delete('inicio_animales')
    cache.delete('buscador_animales')
    cache.delete('animales_count')
    logger.info("Cache de animales invalidado selectivamente")
