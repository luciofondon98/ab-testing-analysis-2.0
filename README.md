# A/B Testing Analysis App

Esta aplicación de Streamlit permite analizar resultados de pruebas A/B, calculando métricas clave de rendimiento y significancia estadística.

## Características

- Análisis de múltiples métricas simultáneamente
- Cálculo de conversión para grupos de control y tratamiento
- Visualización de P2BB (Probability to Be Best)
- Cálculo de mejora relativa
- Análisis de significancia estadística (P-value)
- Interfaz moderna y amigable

## Requisitos

```bash
streamlit
numpy
scipy
plotly
pandas
```

## Uso

1. Ejecuta la aplicación:
```bash
python -m streamlit run app.py
```

2. Ingresa los datos en el siguiente formato:
```
[Nombre de la Métrica]
Baseline [sesiones] [conversiones]
Treatment [sesiones] [conversiones]
```

Ejemplo:
```
Website conversion
Baseline 1000 100
Treatment 1000 120
```

3. Haz clic en "Analizar" para ver los resultados

## Visualización

La aplicación muestra tarjetas métricas con:
- Tasas de conversión para OG y V1
- Gráfico de P2BB
- Porcentaje de mejora
- P-value del test 