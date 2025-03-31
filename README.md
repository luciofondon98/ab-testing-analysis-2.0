# Análisis A/B Testing con Streamlit

Esta aplicación web permite realizar análisis de pruebas A/B, calculando métricas clave de rendimiento (KPIs) y significancia estadística.

## Requisitos

- Windows 10 o superior
- Python 3.x instalado
- Permisos de administrador para la instalación inicial

## Instalación y Uso

### Windows
1. Haz clic derecho en el archivo `iniciar_app_admin.bat`
2. Selecciona "Ejecutar como administrador"
3. La aplicación se abrirá automáticamente en tu navegador web predeterminado

### Linux/Mac
1. Abre una terminal en la carpeta del proyecto
2. Ejecuta:
```bash
chmod +x iniciar_app.sh
./iniciar_app.sh
```

### Formato de Datos
Ingresa los datos en el siguiente formato:
```
[Nombre de la Métrica]
Baseline [sesiones] [conversiones]
treatment [sesiones] [conversiones]
```

Por ejemplo:
```
Website conversion
Baseline 1000 100
treatment 1000 120
```

## Métricas Calculadas

- Tasa de conversión OG (Original/Baseline)
- Tasa de conversión V1 (Variante)
- P-value (usando chi-square test)
- Probabilidad bayesiana (P2BB)
- Porcentaje de mejora/deterioro
- Visualización de probabilidades en gráfico de dona 