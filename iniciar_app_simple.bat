@echo off
echo Iniciando la aplicación de Análisis A/B Testing...
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar si app.py existe
if not exist "app.py" (
    echo Error: No se encontró el archivo app.py
    echo Asegúrate de que el archivo app.py está en el mismo directorio que este script.
    pause
    exit /b 1
)

echo Iniciando la aplicación...
python -m streamlit run app.py
pause 