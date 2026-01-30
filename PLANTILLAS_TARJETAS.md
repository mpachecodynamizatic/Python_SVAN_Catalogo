# Plantillas Dinámicas de Tarjetas de Productos

## Descripción

Se ha implementado un sistema de configuración dinámica que permite definir qué información se muestra en las tarjetas de productos de forma parametrizada por categoría.

## Características Principales

### 1. Jerarquía de Configuración

El sistema utiliza una jerarquía de configuraciones que se aplica en el siguiente orden:

1. **Plantilla específica de subcategoría** - La más específica
2. **Plantilla genérica de categoría** - Se aplica a todas las subcategorías sin configuración específica
3. **Plantilla de catálogo** - Se aplica a todas las categorías del catálogo
4. **Configuración general por defecto** - Se aplica cuando no hay ninguna configuración específica

### 2. Configuración General por Defecto

Cuando no existe ninguna configuración personalizada, el sistema muestra:

**Campos de la ficha del producto:**
- SKU
- Título
- EAN
- Estado
- Color

**Nota:** La marca NO se muestra en la plantilla por defecto.

**Atributos:** Ninguno (el bloque de atributos estará vacío)

### 3. Interfaz de Diseño

En la pantalla de **Fichas** (edición), se ha agregado un botón **"Diseño"** que abre un modal donde puedes:

1. **Ver los atributos disponibles**: El sistema muestra todos los atributos únicos que existen en los productos de esa categoría
2. **Seleccionar atributos**: Mediante checkboxes, puedes seleccionar qué atributos quieres mostrar en las tarjetas
3. **Guardar como genérica**: Opción para guardar la configuración como plantilla genérica de toda la categoría

### 4. Opciones de Guardado

#### Guardar para esta subcategoría específica
- La configuración solo se aplica a la subcategoría actual
- Otras subcategorías de la misma categoría no se verán afectadas

#### Guardar como plantilla genérica de la categoría
- Activando el checkbox "Guardar como plantilla genérica"
- La configuración se aplicará a **todas las subcategorías** de la categoría que no tengan una configuración específica
- Si luego creas una configuración específica para una subcategoría, esa tendrá prioridad sobre la genérica

## Base de Datos

### Tabla: plantilla_tarjeta

```sql
CREATE TABLE plantilla_tarjeta (
    id INTEGER PRIMARY KEY,
    catalogo_id INTEGER NULL,
    categoria_id INTEGER NULL,
    subcategoria_id INTEGER NULL,
    campos_ficha TEXT DEFAULT '["sku", "titulo", "ean", "estado_referencia", "color"]',
    atributos_seleccionados TEXT DEFAULT '[]',
    es_generica BOOLEAN DEFAULT 0,
    FOREIGN KEY (catalogo_id) REFERENCES catalogo(id),
    FOREIGN KEY (categoria_id) REFERENCES categoria(id),
    FOREIGN KEY (subcategoria_id) REFERENCES subcategoria(id)
);
```

### Campos

- **catalogo_id**: ID del catálogo (nullable)
- **categoria_id**: ID de la categoría (nullable)
- **subcategoria_id**: ID de la subcategoría (nullable)
- **campos_ficha**: JSON array con los campos de la ficha a mostrar
- **atributos_seleccionados**: JSON array con los nombres de los atributos seleccionados
- **es_generica**: Booleano que indica si es una plantilla genérica de categoría

## API Endpoints

### GET /obtener_atributos_categoria/<categoria_id>
Obtiene todos los atributos únicos disponibles en los productos de una categoría.

**Respuesta:**
```json
{
    "atributos": ["Potencia", "Capacidad", "Consumo energético", ...]
}
```

### GET /obtener_plantilla_tarjeta/<subcategoria_id>
Obtiene la plantilla activa para una subcategoría (siguiendo la jerarquía).

**Respuesta:**
```json
{
    "campos_ficha": ["sku", "titulo", "ean", "estado_referencia", "color"],
    "atributos_seleccionados": ["Potencia", "Capacidad"]
}
```

### POST /guardar_plantilla_tarjeta
Guarda la configuración de plantilla.

**Cuerpo de la solicitud:**
```json
{
    "subcategoria_id": 123,
    "campos_ficha": ["sku", "titulo", "ean", "estado_referencia", "color"],
    "atributos_seleccionados": ["Potencia", "Capacidad", "Consumo energético"],
    "es_generica": false
}
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Plantilla guardada correctamente"
}
```

## Uso

### Configurar una subcategoría específica

1. Navega a la pantalla de **Fichas** de la subcategoría que deseas configurar
2. Haz clic en el botón **"Diseño"**
3. Se abrirá un modal mostrando todos los atributos disponibles
4. Selecciona los atributos que deseas mostrar en las tarjetas
5. **NO marques** el checkbox "Guardar como plantilla genérica"
6. Haz clic en **"Guardar Plantilla"**
7. La página se recargará y verás los cambios aplicados

### Configurar una plantilla genérica para toda la categoría

1. Navega a cualquier subcategoría de la categoría que deseas configurar
2. Haz clic en el botón **"Diseño"**
3. Selecciona los atributos que deseas mostrar
4. **Marca** el checkbox "Guardar como plantilla genérica para toda la categoría"
5. Haz clic en **"Guardar Plantilla"**
6. La configuración se aplicará a todas las subcategorías de esa categoría que no tengan configuración específica

## Visualización

Las plantillas se aplican en las siguientes pantallas:

1. **Fichas** (pantalla de edición)
2. **Ver Fichas** (pantalla de visualización de una subcategoría)
3. **Ver Categoría Completa** (visualización de todas las subcategorías de una categoría)

## Notas Técnicas

### Función Principal
La función `obtener_plantilla_activa(subcategoria_id)` en `app.py` implementa la lógica de jerarquía:

```python
def obtener_plantilla_activa(subcategoria_id):
    """
    Obtiene la plantilla activa para una subcategoría siguiendo la jerarquía:
    subcategoria > categoria > catalogo > general (default)
    """
    # Busca en orden: subcategoría -> categoría -> catálogo -> general
    # Retorna configuración por defecto si no encuentra ninguna
```

### Templates Actualizados

- `templates/fichas.html` - Agregado botón "Diseño" y modal de configuración
- `templates/ver_fichas.html` - Usa plantilla_config para filtrar atributos
- `templates/ver_categoria_completa.html` - Usa plantilla_config de cada subcategoría

### Filtrado de Atributos

Los templates usan la siguiente lógica para mostrar solo los atributos seleccionados:

```jinja2
{% if plantilla_config.atributos_seleccionados %}
    {% set atributos_mostrar = [] %}
    {% for attr in atributos %}
        {% if attr.atributo in plantilla_config.atributos_seleccionados %}
            {% set _ = atributos_mostrar.append(attr) %}
        {% endif %}
    {% endfor %}
    <!-- Mostrar solo atributos_mostrar -->
{% else %}
    <div class="text-muted">Sin atributos configurados</div>
{% endif %}
```

## Ejemplo de Flujo Completo

### Escenario: Configurar categoría "LAVADORAS"

1. **Configuración genérica de LAVADORAS:**
   - Entrar en cualquier subcategoría de LAVADORAS (ej: "LAVADORA 8KG")
   - Diseño → Seleccionar: "Capacidad", "Rpm", "Clase energética"
   - Marcar "Guardar como genérica"
   - Guardar
   - **Resultado:** Todas las subcategorías de LAVADORAS mostrarán estos 3 atributos

2. **Configuración específica para "LAVADORA CARGA SUP":**
   - Entrar en "LAVADORA CARGA SUP"
   - Diseño → Seleccionar: "Capacidad", "Rpm", "Apertura", "Altura"
   - NO marcar "Guardar como genérica"
   - Guardar
   - **Resultado:** Solo "LAVADORA CARGA SUP" mostrará 4 atributos, las demás subcategorías seguirán mostrando los 3 de la configuración genérica

3. **Sin configuración (ej: nueva categoría "SECADORAS"):**
   - No hay plantilla configurada
   - **Resultado:** Mostrará los campos por defecto (SKU, Título, EAN, Estado, Color) sin ningún atributo adicional
