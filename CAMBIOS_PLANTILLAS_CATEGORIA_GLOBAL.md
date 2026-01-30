# Cambios: Plantillas Genéricas de Categoría Independientes del Catálogo

**Fecha:** 30 de enero de 2026  
**Versión:** 1.2

## Problema Identificado

Las plantillas genéricas de categoría no estaban correctamente implementadas para ser independientes del catálogo. Esto significaba que una categoría que apareciera en múltiples catálogos podría requerir configuraciones separadas para cada uno.

## Solución Implementada

Se ha modificado el sistema para garantizar que **las plantillas genéricas de una categoría se aplican en cualquier catálogo donde esté presente esa categoría**.

## Cambios en el Código

### 1. `app.py` - Función `obtener_plantilla_activa`

**Antes:**
```python
# Buscar plantilla de categoría
plantilla = PlantillaTarjeta.query.filter_by(
    categoria_id=subcategoria.categoria_id, 
    subcategoria_id=None
).first()
```

**Después:**
```python
# Buscar plantilla genérica de categoría (independiente del catálogo)
plantilla = PlantillaTarjeta.query.filter_by(
    categoria_id=subcategoria.categoria_id, 
    subcategoria_id=None,
    catalogo_id=None,
    es_generica=True
).first()
```

### 2. `app.py` - Ruta `guardar_plantilla_categoria`

Se añadió explícitamente `catalogo_id=None` al crear/buscar plantillas:

**Antes:**
```python
PlantillaTarjeta.query.filter_by(
    categoria_id=categoria_id,
    subcategoria_id=None,
    es_generica=True
).delete()

plantilla = PlantillaTarjeta(
    categoria_id=categoria_id,
    subcategoria_id=None,
    ...
)
```

**Después:**
```python
PlantillaTarjeta.query.filter_by(
    categoria_id=categoria_id,
    subcategoria_id=None,
    catalogo_id=None,
    es_generica=True
).delete()

plantilla = PlantillaTarjeta(
    catalogo_id=None,
    categoria_id=categoria_id,
    subcategoria_id=None,
    ...
)
```

### 3. `app.py` - Ruta `obtener_plantilla_categoria`

Se añadió `catalogo_id=None` al filtro:

```python
plantilla = PlantillaTarjeta.query.filter_by(
    categoria_id=categoria_id,
    subcategoria_id=None,
    catalogo_id=None,
    es_generica=True
).first()
```

### 4. `app.py` - Ruta `/categorias`

Se añadió `catalogo_id=None` al verificar plantillas:

```python
tiene_plantilla = PlantillaTarjeta.query.filter_by(
    categoria_id=cat.id,
    subcategoria_id=None,
    catalogo_id=None,
    es_generica=True
).first() is not None
```

## Cambios en la Documentación

### `PLANTILLAS_TARJETAS.md`

Se actualizó para clarificar que las plantillas genéricas de categoría son independientes del catálogo:

1. **Sección Jerarquía:** Se añadió nota explicativa sobre la independencia del catálogo
2. **Sección Guardado:** Se añadió punto indicando que la plantilla será válida para cualquier catálogo
3. **Sección Uso:** Se añadió aclaración sobre la aplicación multi-catálogo
4. **Ejemplo:** Se añadió nota sobre aplicación en todos los catálogos

## Verificación

Se creó el script `test_plantilla_categoria_global.py` que verifica:

- ✅ Las plantillas genéricas tienen `catalogo_id=None`
- ✅ No existen plantillas genéricas con catálogo específico
- ✅ Se identifican todas las subcategorías que heredan la plantilla
- ✅ Se listan los catálogos donde se aplicará la plantilla

## Jerarquía Actualizada

```
1. Plantilla específica de subcategoría (subcategoria_id específico)
2. Plantilla genérica de categoría (categoria_id, catalogo_id=None, es_generica=True)
3. Plantilla de catálogo (catalogo_id específico, categoria_id=None)
4. Configuración general por defecto (todos NULL)
```

## Impacto en el Usuario

### Antes del Cambio

Si la categoría "LAVADORAS" existía en:
- Catálogo "Electrodomésticos 2024"
- Catálogo "Electrodomésticos 2025"

Habría que configurar plantillas separadas para cada catálogo.

### Después del Cambio

Una sola plantilla genérica de "LAVADORAS" se aplica automáticamente en AMBOS catálogos.

## Beneficios

1. **Coherencia:** Una categoría se muestra de la misma manera en todos los catálogos
2. **Simplicidad:** Una sola configuración por categoría
3. **Mantenibilidad:** Actualizar la plantilla de una categoría actualiza todos los catálogos
4. **Eficiencia:** Menos configuraciones a mantener

## Compatibilidad hacia Atrás

Los cambios son **100% compatibles** con configuraciones existentes:

- Plantillas específicas de subcategoría siguen teniendo prioridad
- Plantillas de catálogo siguen funcionando como respaldo
- La configuración general por defecto permanece inalterada
- No se requiere migración de datos

## Archivos Modificados

1. `app.py` (4 funciones/rutas modificadas)
2. `PLANTILLAS_TARJETAS.md` (4 secciones actualizadas)
3. `test_plantilla_categoria_global.py` (nuevo archivo de prueba)

## Próximos Pasos

El sistema está listo para usar. Los administradores pueden:

1. Configurar plantillas genéricas desde la pantalla **Categorías**
2. Las plantillas se aplicarán automáticamente en todos los catálogos
3. Las subcategorías pueden seguir teniendo configuraciones específicas si es necesario
