# Despliegue en Azure App Service

## Pasos para desplegar desde GitHub:

### 1. Crear Azure App Service

En Azure Portal:

1. Busca "App Services" y haz clic en "Crear"
2. Configuración básica:
   - **Suscripción**: Tu suscripción de Azure
   - **Grupo de recursos**: Crear nuevo o usar existente
   - **Nombre**: `python-svan-catalogo` (debe ser único)
   - **Publicar**: Código
   - **Pila del entorno en tiempo de ejecución**: Python 3.11
   - **Región**: West Europe o la más cercana
   - **Plan**: Crear nuevo
     - Nivel de precios: **B1 (Basic)** recomendado o **F1 (Free)** para pruebas

3. Haz clic en "Revisar y crear" y luego "Crear"

### 2. Configurar Deployment desde GitHub

Una vez creado el App Service:

1. Ve a tu App Service en Azure Portal
2. En el menú izquierdo, busca **"Centro de implementación"** (Deployment Center)
3. Configuración:
   - **Origen**: GitHub
   - Autoriza tu cuenta de GitHub si es necesario
   - **Organización**: Tu usuario de GitHub
   - **Repositorio**: Python_SVAN_Catalogo
   - **Rama**: master (o main)
4. Haz clic en "Guardar"

Azure creará automáticamente un GitHub Action en tu repositorio.

### 3. Configurar variables de entorno

En Azure Portal → Tu App Service → **Configuración** → **Configuración de la aplicación**:

Añade estas variables:

- `SECRET_KEY`: genera un valor aleatorio seguro (ejemplo: `tu-clave-secreta-aleatoria-muy-larga`)
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true`
- `WEBSITE_HTTPLOGGING_RETENTION_DAYS`: `7` (opcional, para logs)

### 4. Configurar comando de inicio

En Azure Portal → Tu App Service → **Configuración** → **Configuración general**:

En **Comando de inicio**, pon:
```bash
bash startup.sh
```

Guarda los cambios.

### 5. Verificar deployment

1. Ve a **Centro de implementación** → verás el estado del deployment
2. También puedes ver en tu repositorio de GitHub → Actions
3. Una vez completado, accede a tu app en: `https://python-svan-catalogo.azurewebsites.net`

### 6. Ver logs en tiempo real

Para diagnosticar problemas:

```bash
# Instalar Azure CLI si no lo tienes
az login
az webapp log tail --name python-svan-catalogo --resource-group TU_GRUPO_RECURSOS
```

O en Azure Portal → Tu App Service → **Flujos de registro**

## Persistencia de datos

- ✅ La carpeta `/home/instance` persiste entre deployments
- ✅ La base de datos SQLite se guarda en `/home/instance/catalogos_nuevo.db`
- ✅ Los datos NO se borran al hacer redeploy
- ✅ Backups: puedes configurar backups automáticos en Azure Portal

## Costos estimados

- **Plan F1 (Free)**: Gratis, 60 minutos/día de CPU, 1GB RAM, 1GB almacenamiento
- **Plan B1 (Basic)**: ~€12/mes, siempre activo, 1.75GB RAM, 10GB almacenamiento
- **Plan D1 (Shared)**: ~€8/mes, intermedio entre F1 y B1

## Ventajas sobre Render

- ✅ Persistencia de datos garantizada en `/home`
- ✅ Mejor performance en Europa (región Frankfurt/West Europe)
- ✅ Integración con servicios de Azure
- ✅ Logs más completos y herramientas de diagnóstico
- ✅ Backups automáticos disponibles
- ✅ Escalado horizontal y vertical fácil

## Solución de problemas

### La app no inicia
Ver logs: Azure Portal → App Service → Flujos de registro

### Base de datos se borra
Verificar que `instance_path = '/home/instance'` en los logs de inicio

### Timeout en importaciones grandes
En startup.sh, ajustar `--timeout 600` a un valor mayor si es necesario

## Migrar desde Render

Si ya tienes datos en Render:

1. Descarga la base de datos desde Render (si es posible acceder por SSH o crear un endpoint temporal)
2. Súbela temporalmente a través de una ruta en tu app Flask
3. O mejor: exporta los datos como CSV/JSON y reimporta en Azure

## Alternativa: Usar PostgreSQL

Para aplicaciones en producción, considera migrar a Azure Database for PostgreSQL:

1. Crear Azure Database for PostgreSQL Flexible Server (tier B1ms ~€12/mes)
2. Cambiar en app.py:
   ```python
   db_path = os.environ.get('DATABASE_URL')  # Azure proveerá esto automáticamente
   ```
3. Ventajas: persistencia garantizada, backups automáticos, mejor para múltiples workers
