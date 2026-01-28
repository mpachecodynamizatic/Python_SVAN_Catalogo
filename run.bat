@echo off
echo ================================================
echo  Iniciando Codigos Postales
echo ================================================
echo.

REM Verificar si existe el entorno virtual
if not exist ".venv" (
    echo [INFO] No se encontro el entorno virtual. Creando nuevo entorno...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        echo [INFO] Asegurate de tener Python instalado y en el PATH.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado exitosamente.
    echo.
) else (
    echo [OK] Entorno virtual encontrado.
    echo.
)

REM Activar el entorno virtual
echo [INFO] Activando entorno virtual...
call .\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual.
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado.
echo.

REM Actualizar pip
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip actualizado.
echo.

REM Instalar/Verificar requerimientos
echo [INFO] Verificando e instalando dependencias...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Hubo un problema al instalar las dependencias.
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas correctamente.
    echo.
) else (
    echo [ADVERTENCIA] No se encontro el archivo requirements.txt
    echo.
)

REM Iniciar la aplicacion
echo ================================================
echo  Iniciando aplicacion...
echo ================================================
echo.
echo [INFO] Ejecutando app.py
echo [INFO] Presiona Ctrl+C para detener el script
echo.

python app.py

echo.
echo [OK] Script finalizado
echo.

REM Si el script termina, desactivar el entorno virtual
call .venv\Scripts\deactivate.bat 2>nul
pause
