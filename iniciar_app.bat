@echo off
echo Iniciando la aplicación de Análisis A/B Testing...
echo.
echo Actualizando pip...
python -m pip install --upgrade pip
echo.
echo Instalando dependencias necesarias...
python -m pip install --user streamlit==1.32.0
python -m pip install --user numpy==1.26.4
python -m pip install --user scipy==1.12.0
python -m pip install --user plotly==5.19.0
echo.
echo Iniciando la aplicación...
python -m streamlit run app.py
pause 