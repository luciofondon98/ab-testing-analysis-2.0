#!/bin/bash
echo "Iniciando la aplicación de Análisis A/B Testing..."
echo
echo "Actualizando pip..."
python3 -m pip install --upgrade pip
echo
echo "Instalando dependencias necesarias..."
python3 -m pip install --user streamlit==1.32.0
python3 -m pip install --user numpy==1.26.4
python3 -m pip install --user scipy==1.12.0
python3 -m pip install --user plotly==5.19.0
echo
echo "Iniciando la aplicación..."
python3 -m streamlit run app.py 