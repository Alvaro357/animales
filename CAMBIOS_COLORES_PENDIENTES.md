# Cambios de Colores y Tipografía - Estado Actual

## Objetivo
Cambiar todos los colores de botones, letras y la tipografía a estilo manuscrito cálido con tonos pastel en la aplicación web.

## Paleta de Colores Pastel Cálidos
- **Primario (botones principales)**: `#ffb4a2` (coral pastel)
- **Secundario (botones secundarios)**: `#ffc9d9` (rosa pastel)
- **Acento**: `#ffd89b` (amarillo cálido)
- **Texto principal**: `#ffe4cc` (crema cálido)
- **Texto secundario**: `#ffd4b8` (melocotón claro)
- **Texto oscuro (sobre botones)**: `#5c4a42` (marrón oscuro)

## Tipografía
**Fuente manuscrita**: Pacifico
- URL: `https://fonts.googleapis.com/css2?family=Pacifico&family=Inter:wght@300;400;500;600;700&display=swap`
- CSS: `font-family: 'Pacifico', cursive;`

## Estado de Archivos

### ✅ COMPLETADO
1. **index.html** - Todos los cambios aplicados:
   - ✅ Tipografía cambiada a Pacifico
   - ✅ Color de texto principal: `#ffe4cc`
   - ✅ Estrellas brillantes: `#ffd89b`
   - ✅ Botón primario: gradiente `#ffb4a2` a `#ff9a7f`
   - ✅ Botón secundario: `#ffc9d9` con transparencia
   - ✅ Cards hover: borde `#ffb4a2`
   - ✅ Filtros activos: gradiente coral
   - ✅ Inputs focus: borde `#ffb4a2`
   - ✅ Título principal: gradiente `#ffe4cc` a `#ffb4a2`
   - ✅ Contador de resultados: `#ffd89b`
   - ✅ Spinners: `#ffb4a2`
   - ✅ Contador de favoritos: `#ffc9d9`

### 🔄 EN PROGRESO
2. **mis_animales.html** - Parcialmente completado:
   - ✅ Tipografía cambiada a Pacifico
   - ✅ Color de texto principal: `#ffe4cc`
   - ✅ Estrellas brillantes: `#ffd89b`
   - ✅ Botón primario: gradiente coral
   - ✅ Botón secundario: rosa pastel
   - ✅ Botón danger: gradiente coral
   - ✅ Cards hover: borde coral
   - ✅ Filtros: colores pastel
   - ✅ Search input focus: `#ffb4a2`
   - ✅ Título principal: gradiente crema-coral
   - ❌ **PENDIENTE**: form-input:focus
   - ❌ **PENDIENTE**: form-label
   - ❌ **PENDIENTE**: badge-disponible
   - ❌ **PENDIENTE**: badge-adoptado
   - ❌ **PENDIENTE**: select options
   - ❌ **PENDIENTE**: spinners y loading states
   - ❌ **PENDIENTE**: revisar más estilos

### ⏳ PENDIENTE
3. **mis_favoritos.html** - No iniciado
4. **vista_animal.html** - No iniciado

## Instrucciones para Continuar

### Para mis_animales.html (Completar)
Aplicar los siguientes cambios:

```css
/* Forms */
.form-input:focus {
    border-color: #ffb4a2;
    box-shadow: 0 0 0 3px rgba(255, 180, 162, 0.2);
}

.form-label {
    color: #ffe4cc;
}

/* Badges de estado */
.badge-disponible {
    background: rgba(255, 216, 155, 0.15);
    border: 1px solid rgba(255, 216, 155, 0.3);
    color: #ffd89b;
}

.badge-adoptado {
    background: rgba(255, 201, 217, 0.15);
    border: 1px solid rgba(255, 201, 217, 0.3);
    color: #ffc9d9;
}

/* Select options */
select.form-input option:checked,
select.form-input option:hover {
    background-color: #ffb4a2;
    color: #5c4a42;
}

select.form-input:focus {
    border-color: #ffb4a2;
    box-shadow: 0 0 0 3px rgba(255, 180, 162, 0.2);
}

/* Spinners */
.create-spinner,
.register-spinner {
    border: 3px solid rgba(255, 180, 162, 0.3);
    border-left: 3px solid #ffb4a2;
}

.create-spinner-small,
.register-spinner-small {
    border: 2px solid rgba(255, 180, 162, 0.3);
    border-left: 2px solid #ffb4a2;
}
```

### Para mis_favoritos.html
Aplicar TODOS los cambios de colores siguiendo el patrón de index.html:
1. Cambiar tipografía a Pacifico
2. Cambiar color del body a `#ffe4cc`
3. Actualizar todos los botones, cards, filtros, inputs, etc.

### Para vista_animal.html
Aplicar TODOS los cambios de colores siguiendo el patrón de index.html:
1. Cambiar tipografía a Pacifico
2. Cambiar color del body a `#ffe4cc`
3. Actualizar todos los botones, cards, badges, inputs, etc.

## Notas Importantes
- **NO cambiar el fondo oscuro con estrellas** - Solo cambiar colores de elementos UI
- Mantener coherencia: usar siempre los mismos colores para los mismos tipos de elementos
- La tipografía Pacifico debe aplicarse al body completo
- Todos los azules (#3b82f6, #1d4ed8, #60a5fa) deben cambiarse a coral (#ffb4a2, #ff9a7f)
- Todos los rojos (#ef4444) deben cambiarse a rosa pastel (#ffc9d9) o coral según contexto
- Todos los verdes (#22c55e) deben cambiarse a amarillo cálido (#ffd89b)

## Comando para Reanudar
"Continúa aplicando los cambios de colores pastel y tipografía Pacifico según el archivo CAMBIOS_COLORES_PENDIENTES.md"
