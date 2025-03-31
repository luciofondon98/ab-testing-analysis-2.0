@echo off
echo Verificando permisos de administrador...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Permisos de administrador confirmados.
) else (
    echo Este script requiere permisos de administrador.
    echo Por favor, haz clic derecho en este archivo y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

echo Iniciando la aplicación de Análisis A/B Testing...
echo.
echo Actualizando pip...
python -m pip install --upgrade pip
echo.
echo Instalando dependencias necesarias...
python -m pip install numpy
python -m pip install scipy
python -m pip install streamlit
python -m pip install plotly
echo.
echo Iniciando la aplicación...
python -m streamlit run app.py
pause 