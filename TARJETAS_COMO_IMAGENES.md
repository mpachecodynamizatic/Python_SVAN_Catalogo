# Conversión de Tarjetas a Imágenes en PDF

## Implementación Completada

Se ha modificado el sistema para que las **tarjetas** se conviertan en imágenes antes de insertarlas en el PDF, en lugar de construirlas con elementos de ReportLab.

## Cambios Realizados

### 1. Nuevas Dependencias (`requirements.txt`)
- **Pillow**: Para manipulación de imágenes
- **html2image**: Para convertir HTML a imágenes PNG

### 2. Nuevo Template HTML (`templates/tarjeta_pdf.html`)
Template dedicado que renderiza una tarjeta individual con:
- Diseño de 4 bloques (2x2)
- Bloque superior izquierdo: Imagen del producto
- Bloque superior derecho: Datos comerciales (PVP, ventas, stock, etc.)
- Bloque inferior izquierdo: Datos del producto (SKU, marca, EAN, etc.)
- Bloque inferior derecho: Atributos técnicos
- Pie: Dimensiones y fabricante

### 3. Nueva Función `renderizar_tarjeta_como_imagen()`
```python
def renderizar_tarjeta_como_imagen(producto, dm):
    """Renderiza una tarjeta como imagen HTML usando html2image"""
```

**Proceso:**
1. Prepara los datos del producto y atributos
2. Renderiza el template HTML con los datos
3. Usa `html2image` para convertir el HTML a PNG
4. Guarda en directorio temporal
5. Lee la imagen con PIL
6. Convierte a BytesIO para uso en ReportLab
7. Limpia archivos temporales

### 4. Función `crear_tarjeta_pdf()` Modificada
Ahora tiene dos modos:
1. **Modo principal (nuevo)**: Intenta renderizar como imagen HTML
2. **Modo fallback**: Si falla, usa el código original de ReportLab

## Ventajas de Este Enfoque

✅ **Diseño más fiel**: Las tarjetas en PDF se ven idénticas a las de pantalla  
✅ **Código simplificado**: No hay que recrear el layout con ReportLab  
✅ **CSS completo**: Se pueden usar estilos avanzados de Bootstrap  
✅ **Mantenimiento fácil**: Un solo template para HTML y PDF  
✅ **Fallback seguro**: Si falla, usa el método original

## Desventajas a Considerar

⚠️ **Peso del archivo**: Las imágenes aumentan el tamaño del PDF  
⚠️ **Velocidad**: Generar imágenes es más lento que crear elementos nativos  
⚠️ **Texto no seleccionable**: El contenido de las tarjetas no se puede copiar  
⚠️ **Dependencia de Chrome**: html2image necesita Chrome/Chromium instalado

## Uso

Al generar un PDF de fichas, el sistema automáticamente:
1. Toma cada tarjeta que tenga producto asociado
2. La renderiza como imagen HTML
3. Inserta la imagen en el PDF
4. Si una tarjeta no tiene producto, muestra texto simple

## Configuración de html2image

La biblioteca usa Chrome/Chromium para renderizar. Si no está instalado:

**Windows:**
```bash
# html2image buscará Chrome automáticamente en:
# C:\Program Files\Google\Chrome\Application\chrome.exe
# C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
```

**Si Chrome no está disponible**, se puede especificar manualmente:
```python
hti = Html2Image(
    output_path=temp_dir, 
    size=(400, 300),
    browser_executable='ruta/a/chrome.exe'
)
```

## Probar la Funcionalidad

Genera un PDF desde la interfaz web:
1. Ve a "Ver Fichas" de cualquier subcategoría
2. Haz clic en "Generar PDF"
3. Las tarjetas aparecerán como imágenes en el PDF resultante

## Archivo de Prueba

`test_tarjeta_imagen.py` - Script para probar la generación de una tarjeta individual como imagen.
