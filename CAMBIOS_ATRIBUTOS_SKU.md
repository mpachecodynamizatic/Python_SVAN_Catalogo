# Actualización del Modelo de Datos - Atributos con SKU

## Resumen de Cambios

Se ha actualizado el modelo de datos y la importación de atributos para incluir el campo **SKU** como parte del modelo Atributo.

---

## 1. Cambios en el Modelo de Datos

### Tabla `atributo`
**Nueva columna añadida:**
- `sku` VARCHAR(50) NULL - SKU del producto (redundante para facilitar búsquedas)

**Estructura completa:**
```sql
CREATE TABLE atributo (
    id INTEGER PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    sku VARCHAR(50) NULL,           -- NUEVO CAMPO
    atributo VARCHAR(100) NOT NULL,
    valor VARCHAR(200) NOT NULL,
    orden INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (producto_id) REFERENCES producto(id)
);
```

### Modelo SQLAlchemy actualizado:
```python
class Atributo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    sku = db.Column(db.String(50))  # SKU del producto (redundante para facilitar búsquedas)
    atributo = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.String(200), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    producto = db.relationship('Producto', backref=db.backref('atributos', lazy=True))
```

---

## 2. Cambios en la Importación

### Función `importar_atributos_con_progreso()` actualizada:

**Ahora soporta dos métodos de búsqueda:**

1. **Por SKU directo del CSV** (si existe la columna 'SKU')
   - Búsqueda directa: `Producto.query.filter_by(sku=sku).first()`
   
2. **Por ProductoId** (método tradicional, fallback)
   - Búsqueda por ID CSV: `Producto.query.filter_by(id_csv=producto_id_csv).first()`

**Al importar, se guarda automáticamente:**
- El `sku` del producto encontrado en el campo `atributo.sku`
- Esto permite búsquedas más rápidas y redundancia de datos

---

## 3. CSV Actualizado

### Columnas esperadas en `producto_atributos_PIM.csv`:

**Columnas existentes:**
- `id` - ID del atributo
- `ProductoId` - ID del producto (relación legacy)
- `AtributoId` - ID del tipo de atributo
- `Nombre` - Nombre del atributo
- `Valor` - Valor del atributo
- `Unidad` - Unidad de medida
- `OrdenEnGrupo` - Orden de visualización

**Nueva columna (opcional pero recomendada):**
- `SKU` - SKU del producto (permite búsqueda directa)

**Ejemplo:**
```csv
id;ProductoId;AtributoId;Nombre;Valor;Unidad;OrdenEnGrupo;SKU
1;1644;1178;Alto embalaje;115;mm;24;AI3600SB
2;1644;1180;Alto zonas independientes;;mm;7;AI3600SB
```

---

## 4. Mejoras en Búsqueda

La búsqueda en la pantalla de productos-atributos ahora incluye:
- Nombre del atributo
- Valor del atributo
- **SKU del atributo (nuevo)**
- SKU del producto
- Marca del producto
- Título del producto

---

## 5. Estado Actual de la Base de Datos

**Estadísticas:**
- Total de atributos: **203,194**
- Atributos con SKU: **203,194 (100%)**
- Atributos sin SKU: **0 (0%)**
- Coherencia de datos: **100%** (todos los SKUs coinciden con sus productos)

**Scripts creados:**
- `actualizar_atributos_sku.py` - Migra SKUs de productos a atributos existentes
- `verificar_atributos.py` - Verifica integridad del modelo de datos

---

## 6. Ventajas del Nuevo Modelo

✅ **Búsqueda más rápida**: El SKU en el atributo permite búsquedas sin JOIN
✅ **Redundancia controlada**: Facilita consultas y mantiene integridad referencial
✅ **Compatibilidad**: Funciona con CSV con o sin columna SKU
✅ **Migración completa**: Todos los atributos existentes ya tienen SKU asignado
✅ **Importación flexible**: Busca por SKU primero, luego por ProductoId

---

## 7. Cómo Usar

### Para importar con el nuevo CSV (con columna SKU):
1. Añadir columna `SKU` al CSV de atributos
2. Ir a "Importar Datos" en la aplicación
3. Subir el CSV actualizado
4. La importación usará el SKU para búsqueda directa

### Para importar con CSV legacy (sin columna SKU):
1. Usar el CSV actual sin modificaciones
2. La importación usará ProductoId (método tradicional)
3. El SKU se asignará automáticamente desde el producto encontrado

---

## 8. Verificación

Para verificar el estado del modelo:
```bash
python verificar_atributos.py
```

Para actualizar SKUs en atributos existentes:
```bash
python actualizar_atributos_sku.py
```

---

## Conclusión

El modelo de datos ha sido actualizado exitosamente para incluir el campo SKU en los atributos. La migración se completó para los 203,194 atributos existentes sin pérdida de datos. El sistema ahora soporta importación tanto con CSV nuevos (con SKU) como legacy (sin SKU), manteniendo compatibilidad hacia atrás.
