# Requerimientos Funcionales - Sistema de Gestión de Catálogos SVAN

## 1. INFORMACIÓN GENERAL

### 1.1 Descripción del Sistema
Aplicación web desarrollada en Flask para la gestión integral de catálogos de productos de electrodomésticos de las marcas ASPES, WONDER, SVAN, HYUNDAI, NILSON y FAGOR. El sistema permite organizar productos en catálogos jerárquicos, gestionar sus atributos técnicos, imágenes y datos operativos.

### 1.2 Objetivo
Centralizar la gestión de productos y catálogos, facilitando la importación masiva de datos, organización jerárquica de productos y consulta eficiente de información técnica y comercial.

### 1.3 Alcance
- Gestión de catálogos, categorías y subcategorías
- Administración de productos y atributos técnicos
- Importación masiva de datos desde CSV
- Sistema de fichas con tarjetas de productos
- Gestión de imágenes de productos
- Datos manuales (inventario, ventas, precios)
- Sistema de autenticación de usuarios

---

## 2. MÓDULOS FUNCIONALES

### 2.1 MÓDULO DE AUTENTICACIÓN Y SEGURIDAD

#### RF-001: Inicio de Sesión
**Descripción:** Sistema de autenticación de usuarios con credenciales.  
**Prioridad:** Alta  
**Actores:** Usuario, Administrador  

**Criterios de Aceptación:**
- Usuario puede ingresar con nombre de usuario y contraseña
- Contraseñas almacenadas con hash seguro
- Redirección automática a página principal tras login exitoso
- Mensajes de error claros para credenciales incorrectas
- Protección de rutas mediante decorador @login_required

**Usuarios del Sistema:**
- admin (Administrador)
- user (Usuario estándar)
- producto (Usuario de productos)

#### RF-002: Cierre de Sesión
**Descripción:** Usuario puede cerrar sesión de forma segura.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Botón de cierre de sesión visible en todas las páginas
- Limpieza completa de sesión
- Redirección a página de login

---

### 2.2 MÓDULO DE GESTIÓN DE CATÁLOGOS

#### RF-003: Visualización de Catálogos
**Descripción:** Listado principal de todos los catálogos disponibles.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Mostrar código, descripción y marcas de cada catálogo
- Opciones para configurar, ver completo y eliminar catálogos
- Acceso a funcionalidad de crear nuevo catálogo

#### RF-004: Crear Catálogo
**Descripción:** Permite crear un nuevo catálogo con código único, descripción y marcas asociadas.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Formulario con campos: código, descripción y marcas (separadas por coma)
- Código único (no duplicado)
- Validación de campos obligatorios
- Confirmación visual tras creación exitosa

#### RF-005: Copiar Catálogo
**Descripción:** Duplicar un catálogo existente con toda su estructura.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Copia completa de categorías, subcategorías, fichas y tarjetas
- Generar nuevo código único para la copia
- Mantener todas las relaciones internas

#### RF-006: Editar Catálogo
**Descripción:** Modificar información básica de un catálogo existente.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Editar descripción y marcas
- No permitir cambio de código (campo único)
- Actualización inmediata en base de datos

#### RF-007: Eliminar Catálogo
**Descripción:** Eliminar un catálogo y toda su estructura asociada.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Confirmación antes de eliminar
- Eliminación en cascada de categorías, subcategorías, fichas y tarjetas
- Mensaje de confirmación tras eliminación

#### RF-008: Ver Catálogo Completo
**Descripción:** Visualización completa de la estructura jerárquica del catálogo.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Mostrar todas las categorías con sus subcategorías
- Contador de fichas por subcategoría
- Navegación a vista detallada de cada categoría

---

### 2.3 MÓDULO DE GESTIÓN DE CATEGORÍAS

#### RF-009: Configurar Categorías
**Descripción:** Administración de categorías dentro de un catálogo.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Listado de categorías del catálogo seleccionado
- Opción para agregar, eliminar y ver categorías
- Mostrar código y descripción de cada categoría

#### RF-010: Agregar Categoría
**Descripción:** Crear nueva categoría dentro de un catálogo.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Formulario con código y descripción
- Validación de código único dentro del catálogo
- Asociación automática con el catálogo padre

#### RF-011: Eliminar Categoría
**Descripción:** Eliminar categoría y sus elementos asociados.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Confirmación antes de eliminar
- Eliminación en cascada de subcategorías, fichas y tarjetas
- Actualización automática de la vista

#### RF-012: Ver Categoría Completa
**Descripción:** Vista detallada de todas las subcategorías de una categoría.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Listado completo de subcategorías
- Contador de fichas por subcategoría
- Navegación a vista de fichas

---

### 2.4 MÓDULO DE GESTIÓN DE SUBCATEGORÍAS

#### RF-013: Gestionar Subcategorías
**Descripción:** Administración de subcategorías dentro de una categoría.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Listado de subcategorías con código y descripción
- Opciones para agregar, copiar, eliminar y ver fichas
- Sistema de validación predefinido por categoría padre

**Subcategorías Predefinidas por Categoría:**
- AGUA CALIENTE: AEROTERMO, CALENTADOR ATMOSF, CALENTADOR ESTANCO, MONOBLOC, TERMOS
- CAMPANAS: CAMPANA DECORATIVA, CAMPANA EXTRAIBLE, CAMPANA INT, etc.
- CLIMATIZACION: CASSETTE INT, CONDUCTO, SPLIT, etc.
- COCCION: ENCIMERAS DE GAS, HORNOS, INDUCCIONES, MW, VITROCERAMICAS
- (Y 18 categorías más con sus respectivas subcategorías)

#### RF-014: Agregar Subcategoría
**Descripción:** Crear nueva subcategoría validando contra lista predefinida.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Selector desplegable con subcategorías válidas según categoría padre
- Prevención de duplicados
- Asociación automática con categoría padre

#### RF-015: Copiar Subcategoría
**Descripción:** Duplicar subcategoría existente con todas sus fichas y tarjetas.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Copia completa de estructura de fichas y tarjetas
- Mantener todas las relaciones de productos
- Generar ID único para la nueva subcategoría

#### RF-016: Eliminar Subcategoría
**Descripción:** Eliminar subcategoría y elementos asociados.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Confirmación antes de eliminar
- Eliminación en cascada de fichas y tarjetas
- Mensaje de confirmación

---

### 2.5 MÓDULO DE GESTIÓN DE FICHAS Y TARJETAS

#### RF-017: Ver Fichas de Subcategoría
**Descripción:** Visualización de fichas (filas) con sus tarjetas de productos.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Listado de fichas numeradas secuencialmente
- Mostrar hasta 6 tarjetas por ficha (una por marca)
- Tarjetas organizadas por marca: AS, WD, SV, HY, NL, FR
- Indicadores visuales de tarjetas vacías

**Estructura de Tarjeta:**
- Marca del producto
- Imagen del producto
- Nombre/descripción
- Valor energético
- Peso
- Volumen

#### RF-018: Agregar Fila/Ficha
**Descripción:** Crear nueva fila (ficha) dentro de una subcategoría.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Numeración automática secuencial
- Inicializar con 6 espacios vacíos para tarjetas
- Asociación con subcategoría padre

#### RF-019: Eliminar Fila/Ficha
**Descripción:** Eliminar fila y todas sus tarjetas.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Confirmación antes de eliminar
- Eliminación de todas las tarjetas asociadas
- Actualización de numeración de filas

#### RF-020: Búsqueda AJAX de Productos
**Descripción:** Búsqueda dinámica de productos al agregar tarjetas.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Búsqueda en tiempo real mientras el usuario escribe
- Buscar por: SKU, marca, título, descripción, categoría
- Filtrado automático por marca según posición de tarjeta
- Resultados limitados a 10 sugerencias
- Mostrar SKU, marca, título y categoría en resultados

#### RF-021: Agregar Tarjeta a Ficha
**Descripción:** Asociar producto a una posición específica en una ficha.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Validar que la marca del producto coincida con la posición
- Extraer automáticamente atributos: valor energético, peso, volumen
- Asociar producto_id para trazabilidad
- Generar URL de imagen automáticamente
- Una tarjeta por posición de marca en cada fila

#### RF-022: Eliminar Tarjeta
**Descripción:** Remover tarjeta de una ficha dejando espacio vacío.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Mantener espacio vacío para nueva tarjeta
- No afectar otras tarjetas de la misma fila
- Confirmación de eliminación

#### RF-023: Ver Fichas Completas
**Descripción:** Vista detallada de todas las fichas con información completa de tarjetas.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Mostrar todas las fichas con tarjetas pobladas
- Información completa de cada tarjeta
- Vista optimizada para revisión y control de calidad

---

### 2.6 MÓDULO DE GESTIÓN DE PRODUCTOS

#### RF-024: Listar Productos
**Descripción:** Listado paginado de todos los productos con búsqueda y contadores.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Paginación de 50 productos por página
- Búsqueda por: SKU, marca, título, descripción, EAN, categoría
- Mostrar: marca, SKU, categoría, título, descripción
- Contador de atributos por producto
- Total de productos en el sistema

#### RF-025: Ver Detalle de Producto
**Descripción:** Vista completa de información de un producto específico.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Información general: marca, SKU, EAN, categoría
- Descripciones: corta y larga
- Especificaciones técnicas completas
- Imagen principal del producto
- Listado de atributos ordenados
- Datos manuales asociados (si existen)
- Estado y clasificación del producto

#### RF-026: Eliminar Producto
**Descripción:** Eliminar producto y todos sus datos asociados.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Confirmación antes de eliminar
- Eliminación en cascada de atributos e imágenes
- Mantener integridad de tarjetas asociadas
- Mensaje de confirmación

---

### 2.7 MÓDULO DE GESTIÓN DE ATRIBUTOS

#### RF-027: Listar Atributos de Productos
**Descripción:** Listado paginado de todos los atributos con información del producto asociado.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Paginación de 100 atributos por página
- Búsqueda por: nombre atributo, valor, SKU, marca
- Mostrar: producto (SKU, marca, título), atributo, valor
- Ordenación por SKU y orden de atributo
- Total de atributos en el sistema

#### RF-028: Ver Atributos de Producto
**Descripción:** Listado de atributos de un producto específico.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Atributos ordenados según campo 'orden'
- Mostrar nombre y valor de cada atributo
- Opción para eliminar atributos individuales
- Agrupación visual por tipo de atributo

#### RF-029: Eliminar Atributo
**Descripción:** Eliminar atributo específico de un producto.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Confirmación antes de eliminar
- No afectar otros atributos del producto
- Actualización inmediata de la vista

---

### 2.8 MÓDULO DE DATOS MANUALES

#### RF-030: Listar Datos Manuales
**Descripción:** Gestión de datos operativos y comerciales de productos.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Paginación de 50 registros por página
- Búsqueda por SKU o fabricante
- Mostrar: SKU, fabricante, unidades vendidas, PVP, inventario
- Información de entrada: fecha y unidades
- Total de registros en el sistema

**Campos Gestionados:**
- SKU del producto
- Unidades vendidas
- PVP (Precio de Venta Público)
- Inventario actual
- Fecha de entrada
- Unidades de entrada
- Fabricante

---

### 2.9 MÓDULO DE IMPORTACIÓN DE DATOS

#### RF-031: Importar Productos desde CSV
**Descripción:** Importación masiva de productos desde archivo CSV con barra de progreso en tiempo real.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Formato CSV con separador punto y coma (;)
- Codificación UTF-8 con BOM
- Validación de marcas permitidas
- Prevención de duplicados por SKU e id_csv
- Progreso en tiempo real con Server-Sent Events
- Commits parciales cada 100 registros
- Sistema de reintentos automático ante errores
- Generación automática de URLs de imágenes
- Reporte final: importados vs. omitidos

**Campos CSV Requeridos:**
- id, Marca, ProductoId, Sku, Categoria, Ean
- Descripcion, Titulo, DescripcionLarga
- EstadoReferencia, Clasificacion, Color, Dimensiones

**Mapeo de Marcas:**
- ASPES/Aspes → AS
- WONDER/Wonder → WD
- SVAN/Svan → SV
- HYUNDAI/Hyundai → HY
- NILSON/Nilson → NL
- FAGOR/Fagor → FR

#### RF-032: Importar Atributos desde CSV
**Descripción:** Importación masiva de atributos técnicos desde archivo CSV.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Formato CSV con separador punto y coma (;)
- Codificación UTF-8 con BOM
- Relación con productos existentes por ProductoId o SKU
- Prevención de duplicados por combinación (producto, atributo, valor)
- Progreso en tiempo real
- Commits parciales cada 100 registros
- Respeto del orden de atributos (OrdenEnGrupo)
- Asociación automática del SKU del producto

**Campos CSV Requeridos:**
- ProductoId o SKU
- Nombre (nombre del atributo)
- Valor
- OrdenEnGrupo

#### RF-033: Generar Datos Manuales Automáticamente
**Descripción:** Generación automática de datos manuales para productos sin datos manuales previos.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Crear registro para cada producto sin datos manuales
- Valores predeterminados: 0 para numéricos, vacío para textos
- Progreso en tiempo real
- Commits parciales cada 100 registros
- Prevención de duplicados por SKU

#### RF-034: Visualización de Progreso de Importación
**Descripción:** Interface de progreso en tiempo real para operaciones de importación.  
**Prioridad:** Alta  

**Criterios de Aceptación:**
- Barra de progreso visual con porcentaje
- Contador de registros procesados / total
- Contador de registros importados
- Contador de registros omitidos
- Keep-alive cada 2 registros para mantener conexión
- Actualización cada 100 registros procesados
- Mensajes de inicio y completado
- Manejo de errores con mensajes descriptivos

#### RF-035: Consulta de Conteos Previos
**Descripción:** API para obtener totales actuales antes de importar.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Endpoint JSON con conteos actuales
- Productos, atributos y datos manuales
- Respuesta inmediata sin procesamiento pesado

---

### 2.10 MÓDULO DE GESTIÓN DE DATOS

#### RF-036: Eliminar Datos del Sistema
**Descripción:** Operaciones de limpieza masiva de datos.  
**Prioridad:** Media  

**Criterios de Aceptación:**
- Confirmación obligatoria antes de ejecutar
- Opciones separadas para:
  - Eliminar todos los productos y atributos
  - Eliminar todos los catálogos y estructura
  - Eliminar todos los datos manuales
- Mensaje de confirmación tras operación exitosa
- Operación atómica con rollback en caso de error

---

## 3. REQUERIMIENTOS DE DATOS

### 3.1 Modelo de Datos

#### Entidad: Catalogo
**Descripción:** Catálogo principal que agrupa categorías.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- codigo (STRING(50), UNIQUE, NOT NULL)
- descripcion (STRING(200), NOT NULL)
- marcas (STRING(200), NOT NULL) - Separadas por coma

**Relaciones:**
- Uno a muchos con Categoria

#### Entidad: Categoria
**Descripción:** Categoría de productos dentro de un catálogo.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- catalogo_id (INTEGER, FK → Catalogo.id, NOT NULL)
- cod_categoria (STRING(50), NOT NULL)
- descripcion (STRING(200), NOT NULL)

**Relaciones:**
- Muchos a uno con Catalogo
- Uno a muchos con Subcategoria

#### Entidad: Subcategoria
**Descripción:** Subcategoría de productos dentro de una categoría.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- categoria_id (INTEGER, FK → Categoria.id, NOT NULL)
- cod_categoria (STRING(50), NOT NULL)
- descripcion (STRING(200), NOT NULL)

**Relaciones:**
- Muchos a uno con Categoria
- Uno a muchos con Ficha

#### Entidad: Ficha
**Descripción:** Fila dentro de una subcategoría que contiene tarjetas de productos.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- subcategoria_id (INTEGER, FK → Subcategoria.id, NOT NULL)
- fila_numero (INTEGER, NOT NULL)

**Relaciones:**
- Muchos a uno con Subcategoria
- Uno a muchos con Tarjeta

#### Entidad: Tarjeta
**Descripción:** Tarjeta de producto dentro de una ficha.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- ficha_id (INTEGER, FK → Ficha.id, NOT NULL)
- producto_id (INTEGER, FK → Producto.id, NULLABLE)
- marca (STRING(10), NOT NULL)
- imagen (STRING(200), NULLABLE)
- nombre (STRING(200), NULLABLE)
- valor_energetico (STRING(50), NULLABLE)
- peso (STRING(50), NULLABLE)
- volumen (STRING(50), NULLABLE)

**Relaciones:**
- Muchos a uno con Ficha
- Muchos a uno con Producto

#### Entidad: Producto
**Descripción:** Producto del catálogo.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- id_csv (INTEGER, UNIQUE, NOT NULL) - ID del CSV
- marca (STRING(10), NOT NULL) - AS, WD, SV, HY, NL, FR
- producto_id (STRING(50), NULLABLE)
- sku (STRING(50), NULLABLE)
- categoria (STRING(100), DEFAULT '')
- ean (STRING(50), NULLABLE)
- descripcion (TEXT, NULLABLE)
- titulo (TEXT, NULLABLE)
- descripcion_larga (TEXT, NULLABLE)
- estado_referencia (STRING(50), NULLABLE)
- clasificacion (STRING(50), NULLABLE)
- color (STRING(100), NULLABLE)
- dimensiones (STRING(100), NULLABLE)
- imagen (STRING(500), NULLABLE) - URL de imagen principal

**Relaciones:**
- Uno a muchos con Atributo
- Uno a muchos con Imagen
- Uno a muchos con Tarjeta
- Uno a uno con DatosManuales

#### Entidad: Atributo
**Descripción:** Atributos técnicos de productos.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- producto_id (INTEGER, FK → Producto.id, NOT NULL)
- sku (STRING(50), NULLABLE) - Redundante para búsquedas
- atributo (STRING(100), NOT NULL)
- valor (STRING(200), NOT NULL)
- orden (INTEGER, NOT NULL, DEFAULT 0)

**Relaciones:**
- Muchos a uno con Producto

#### Entidad: Imagen
**Descripción:** URLs de imágenes adicionales de productos.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- producto_id (INTEGER, FK → Producto.id, NOT NULL)
- url (STRING(500), NOT NULL)

**Relaciones:**
- Muchos a uno con Producto

#### Entidad: DatosManuales
**Descripción:** Datos operativos y comerciales ingresados manualmente.  
**Atributos:**
- id (INTEGER, PK, auto-increment)
- sku (STRING(50), UNIQUE, NOT NULL)
- unidades_vendidas (INTEGER, DEFAULT 0)
- pvp (FLOAT, DEFAULT 0.0)
- inventario (INTEGER, DEFAULT 0)
- fecha_entrada (STRING(20), NULLABLE) - Formato DD/MM/YYYY
- unidades_entrada (INTEGER, DEFAULT 0)
- fabricante (STRING(100), NULLABLE)

**Relaciones:**
- Relación lógica con Producto por SKU

---

## 4. REQUERIMIENTOS NO FUNCIONALES

### 4.1 Rendimiento
- **RNF-001:** El sistema debe soportar importación de hasta 10,000 productos sin degradación significativa
- **RNF-002:** Las búsquedas AJAX deben responder en menos de 500ms
- **RNF-003:** La paginación debe cargar páginas en menos de 1 segundo
- **RNF-004:** Commits parciales cada 100 registros para evitar bloqueos largos de base de datos

### 4.2 Escalabilidad
- **RNF-005:** Base de datos SQLite para desarrollo, migrable a PostgreSQL/MySQL para producción
- **RNF-006:** Sistema de reintentos automático (hasta 5 intentos) para operaciones de base de datos
- **RNF-007:** Manejo de archivos grandes con límite de campo CSV aumentado

### 4.3 Usabilidad
- **RNF-008:** Interfaz web responsive para diferentes tamaños de pantalla
- **RNF-009:** Mensajes flash claros para todas las operaciones (éxito, error, advertencia)
- **RNF-010:** Barra de progreso visual en operaciones largas (importaciones)
- **RNF-011:** Búsqueda en tiempo real con retroalimentación inmediata

### 4.4 Seguridad
- **RNF-012:** Contraseñas almacenadas con hash usando Werkzeug Security
- **RNF-013:** Sesiones seguras con SECRET_KEY configurable
- **RNF-014:** Protección de rutas mediante decorador @login_required
- **RNF-015:** Validación de archivos subidos (solo CSV)
- **RNF-016:** Nombres de archivo seguros usando secure_filename

### 4.5 Mantenibilidad
- **RNF-017:** Código modular con separación de responsabilidades
- **RNF-018:** Decorador de reintentos reutilizable para operaciones de BD
- **RNF-019:** Logging de operaciones críticas (imports, errores)
- **RNF-020:** Sistema de diagnóstico de disco persistente para despliegues

### 4.6 Disponibilidad
- **RNF-021:** Base de datos con persistencia en disco
- **RNF-022:** Verificación de persistencia de datos entre despliegues
- **RNF-023:** Inicialización automática de base de datos al arrancar
- **RNF-024:** Creación automática de tablas faltantes sin pérdida de datos

### 4.7 Portabilidad
- **RNF-025:** Configuración flexible vía variables de entorno
- **RNF-026:** Compatible con despliegue en Render.com
- **RNF-027:** Soporte para rutas de instancia configurables
- **RNF-028:** Scripts de build automatizados (build.sh)

---

## 5. RESTRICCIONES Y LIMITACIONES

### 5.1 Marcas Permitidas
El sistema solo acepta productos de las siguientes marcas:
- ASPES (código: AS)
- WONDER (código: WD)
- SVAN (código: SV)
- HYUNDAI (código: HY)
- NILSON (código: NL)
- FAGOR (código: FR)

### 5.2 Estructura de Fichas
- Máximo 6 tarjetas por ficha (una por marca)
- Orden fijo de marcas: AS, WD, SV, HY, NL, FR
- Una tarjeta por marca por fila

### 5.3 Formato de Archivos
- CSV con codificación UTF-8 con BOM
- Separador: punto y coma (;)
- Campos de texto pueden contener HTML o formato largo

### 5.4 URLs de Imágenes
- Patrón fijo: `https://pim.gruposvan.com/multimedia/{sku}/800x600_imagen_principal.png`
- Generación automática basada en SKU
- Sin validación de existencia de imagen

### 5.5 Base de Datos
- SQLite en desarrollo y producción (Render.com)
- Límite de concurrencia de SQLite aplicable
- Sistema de reintentos para mitigar problemas de bloqueo

---

## 6. CASOS DE USO PRINCIPALES

### CU-001: Importar Catálogo Completo
**Actor:** Administrador  
**Precondición:** Archivos CSV de productos y atributos disponibles  
**Flujo Principal:**
1. Usuario accede a módulo de importación
2. Selecciona "Importar Productos"
3. Carga archivo CSV de productos
4. Sistema valida formato y procesa importación con progreso visual
5. Al completar, selecciona "Importar Atributos"
6. Carga archivo CSV de atributos
7. Sistema relaciona atributos con productos y muestra progreso
8. Sistema genera datos manuales automáticamente
9. Usuario verifica totales importados

**Postcondición:** Productos y atributos disponibles en el sistema

### CU-002: Crear Catálogo con Estructura Completa
**Actor:** Usuario  
**Precondición:** Productos ya importados  
**Flujo Principal:**
1. Usuario crea nuevo catálogo con código y descripción
2. Agrega categorías al catálogo
3. Para cada categoría, agrega subcategorías desde lista predefinida
4. Para cada subcategoría, agrega filas (fichas)
5. En cada fila, busca y agrega productos por marca
6. Sistema asocia automáticamente atributos de cada producto
7. Usuario revisa vista completa del catálogo

**Postcondición:** Catálogo completo listo para consulta

### CU-003: Consultar Producto con Todos sus Datos
**Actor:** Usuario  
**Precondición:** Productos y datos manuales importados  
**Flujo Principal:**
1. Usuario busca producto por SKU o descripción
2. Selecciona producto de resultados
3. Sistema muestra:
   - Información general (marca, SKU, EAN, categoría)
   - Descripciones corta y larga
   - Imagen principal
   - Todos los atributos técnicos ordenados
   - Datos manuales (ventas, inventario, PVP)
4. Usuario puede editar datos manuales o eliminar producto

**Postcondición:** Usuario obtiene información completa del producto

---

## 7. INTERFACES

### 7.1 Interfaz de Usuario
- Framework: HTML5 + Bootstrap (implícito por estructura de templates)
- Navegación jerárquica: Catálogos → Categorías → Subcategorías → Fichas
- Búsquedas con filtros en todas las vistas de listado
- Paginación en listados grandes
- Modales para confirmaciones de eliminación
- Formularios con validación client-side y server-side

### 7.2 Interfaz de Importación
- Carga de archivos mediante formularios multipart
- Barra de progreso con Server-Sent Events (SSE)
- Keep-alive para mantener conexión durante procesos largos
- Retroalimentación en tiempo real de registros procesados

### 7.3 Interfaz de Búsqueda AJAX
- Autocompletado con debounce
- Resultados filtrados por contexto (marca en tarjetas)
- Máximo 10 resultados por búsqueda
- Información relevante en cada resultado

---

## 8. REGLAS DE NEGOCIO

### RN-001: Validación de Marcas
Solo productos de marcas autorizadas (AS, WD, SV, HY, NL, FR) pueden ser importados o gestionados.

### RN-002: Unicidad de SKU
Cada producto debe tener un SKU único en el sistema. No se permiten duplicados.

### RN-003: Asociación Marca-Tarjeta
Una tarjeta en una posición específica solo puede contener productos de la marca correspondiente a esa posición.

### RN-004: Orden de Tarjetas
El orden de marcas en las fichas es fijo: AS, WD, SV, HY, NL, FR (posiciones 0 a 5).

### RN-005: Subcategorías Predefinidas
Las subcategorías deben corresponder a las listas predefinidas según su categoría padre.

### RN-006: Integridad Referencial
La eliminación de entidades padres debe eliminar en cascada todas las entidades hijas relacionadas.

### RN-007: Generación de URLs de Imágenes
Las URLs de imágenes de productos se generan automáticamente usando el patrón:  
`https://pim.gruposvan.com/multimedia/{SKU}/800x600_imagen_principal.png`

### RN-008: Prevención de Duplicados
Durante la importación, se omiten productos con SKU o id_csv ya existentes en el sistema.

### RN-009: Orden de Atributos
Los atributos se ordenan según el campo "orden" que proviene del campo "OrdenEnGrupo" del CSV.

### RN-010: Datos Manuales por SKU
Los datos manuales se relacionan con productos únicamente por SKU, no por ID interno.

---

## 9. GLOSARIO

- **Catálogo:** Agrupación principal de productos organizada en categorías
- **Categoría:** División de primer nivel dentro de un catálogo (ej: COCCION, LAVADORAS)
- **Subcategoría:** División de segundo nivel dentro de una categoría (ej: INDUCCIONES, VITROCERAMICAS)
- **Ficha:** Fila dentro de una subcategoría que contiene hasta 6 tarjetas de productos
- **Tarjeta:** Representación visual de un producto dentro de una ficha, asociada a una marca específica
- **SKU (Stock Keeping Unit):** Código único que identifica un producto
- **EAN:** Código de barras europeo del producto
- **Atributo:** Característica técnica de un producto (ej: Potencia, Capacidad, Dimensiones)
- **Datos Manuales:** Información operativa y comercial de productos (ventas, inventario, precios)
- **CSV:** Formato de archivo de texto para intercambio de datos (Comma/Semicolon Separated Values)
- **SSE (Server-Sent Events):** Tecnología para enviar actualizaciones en tiempo real del servidor al cliente
- **PIM (Product Information Management):** Sistema de gestión de información de productos

---

## 10. DEPENDENCIAS EXTERNAS

### 10.1 Frameworks y Librerías
- **Flask 2.3.3:** Framework web principal
- **Flask-SQLAlchemy:** ORM para gestión de base de datos
- **Werkzeug:** Utilidades WSGI, seguridad de contraseñas
- **Pillow:** Procesamiento de imágenes
- **Requests:** Cliente HTTP para peticiones externas

### 10.2 Servicios Externos
- **PIM Grupo SVAN:** Servidor de imágenes de productos
  - Base URL: `https://pim.gruposvan.com/multimedia/`
  - Formato de imágenes: PNG 800x600

### 10.3 Infraestructura
- **Render.com:** Plataforma de despliegue en producción
- **Gunicorn:** Servidor WSGI para producción
- **SQLite:** Base de datos embebida

---

## 11. HISTORIAS DE USUARIO COMPLEMENTARIAS

### HU-001: Como administrador, quiero importar miles de productos de forma eficiente
**Criterios de Aceptación:**
- Importación con barra de progreso visual
- Sin timeouts en importaciones grandes
- Reporte de productos importados vs. omitidos
- Capacidad de importar 10,000+ productos

### HU-002: Como usuario, quiero buscar productos rápidamente mientras armo catálogos
**Criterios de Aceptación:**
- Búsqueda en tiempo real (AJAX)
- Resultados filtrados por marca cuando aplique
- Búsqueda por múltiples campos (SKU, descripción, categoría)
- Máximo 10 resultados para no sobrecargar

### HU-003: Como usuario, quiero copiar catálogos existentes para crear versiones nuevas
**Criterios de Aceptación:**
- Copia completa de estructura: categorías, subcategorías, fichas y tarjetas
- Generación de código único para el nuevo catálogo
- Mantenimiento de todas las relaciones de productos

### HU-004: Como administrador, quiero ver el progreso de importaciones largas
**Criterios de Aceptación:**
- Barra de progreso con porcentaje
- Contador de registros procesados
- Información de registros importados vs. omitidos
- Sin congelamientos de pantalla

### HU-005: Como usuario, quiero ver toda la información de un producto en un solo lugar
**Criterios de Aceptación:**
- Información general (marca, SKU, EAN, categoría)
- Descripciones completas
- Imagen principal
- Atributos técnicos ordenados
- Datos operativos (ventas, inventario, precio)

---

## 12. MATRIZ DE TRAZABILIDAD

| Módulo | Requerimientos Funcionales | Prioridad | Estado |
|--------|---------------------------|-----------|--------|
| Autenticación | RF-001, RF-002 | Alta | Implementado |
| Catálogos | RF-003 a RF-008 | Alta | Implementado |
| Categorías | RF-009 a RF-012 | Alta | Implementado |
| Subcategorías | RF-013 a RF-016 | Alta | Implementado |
| Fichas y Tarjetas | RF-017 a RF-023 | Alta | Implementado |
| Productos | RF-024 a RF-026 | Alta | Implementado |
| Atributos | RF-027 a RF-029 | Alta | Implementado |
| Datos Manuales | RF-030 | Alta | Implementado |
| Importación | RF-031 a RF-035 | Alta | Implementado |
| Gestión de Datos | RF-036 | Media | Implementado |

---

## 13. NOTAS TÉCNICAS ADICIONALES

### 13.1 Sistema de Reintentos
- Implementado mediante decorador `@retry_on_db_error`
- Máximo 5 reintentos por defecto
- Delay inicial de 0.5-1 segundo con backoff exponencial
- Rollback automático antes de cada reintento

### 13.2 Optimizaciones de Rendimiento
- Carga de datos en memoria para validaciones masivas durante importación
- Commits parciales cada 100 registros
- Uso de `with_entities` para consultas ligeras
- Subconsultas para conteos eficientes

### 13.3 Manejo de Archivos CSV
- Aumento de límite de tamaño de campo: `csv.field_size_limit(sys.maxsize)`
- Lectura con codificación UTF-8 con BOM
- Procesamiento línea por línea para eficiencia de memoria

### 13.4 Persistencia de Datos
- Archivo de verificación: `DISK_PERSISTENCE_TEST.txt`
- Contador de despliegues para validar persistencia
- Diagnóstico completo al arrancar aplicación
- Verificación de permisos de escritura

### 13.5 Migraciones de Base de Datos
- Columna 'categoria' agregada dinámicamente si no existe
- Sistema compatible con bases de datos existentes
- `db.create_all()` solo crea tablas faltantes, no destruye datos

---

## CONCLUSIÓN

Este documento describe de manera exhaustiva los requerimientos funcionales del Sistema de Gestión de Catálogos SVAN. El sistema proporciona una solución completa para la administración de productos de electrodomésticos, desde la importación masiva de datos hasta la organización jerárquica en catálogos consultables. La arquitectura modular y las optimizaciones de rendimiento permiten manejar grandes volúmenes de datos manteniendo una experiencia de usuario fluida.

---

**Versión:** 1.0  
**Fecha:** 30 de enero de 2026  
**Autor:** Generado por análisis del código fuente  
**Estado:** Documento Completo
