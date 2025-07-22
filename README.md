# 📊 A/B/N Testing Analysis Tool 2.0

Una aplicación web interactiva construida con Streamlit para analizar pruebas A/B/N con múltiples variantes. Proporciona análisis estadístico completo, visualizaciones interactivas y comparaciones detalladas entre todas las variantes.

## 🚀 Características Principales

### ✨ Análisis Multivariante Completo
- **Soporte A/B/N**: Analiza cualquier número de variantes (no solo A/B)
- **Test Chi-cuadrado**: Análisis global de significancia estadística
- **Comparaciones pareadas**: Cada variante vs control y entre todas las variantes
- **Análisis Bayesiano**: Probabilidad de superar (P2BB)

### 📋 Matriz de Comparaciones Interactiva
- **Vista panorámica**: Todas las comparaciones en una sola matriz
- **Tooltips detallados**: Información completa al pasar el cursor
- **Códigos de colores**: Identificación visual inmediata de resultados
- **Datos completos**: Tasas de conversión, lift, p-values, y significancia

### 📊 Visualizaciones Potentes
- **Gráficos interactivos**: Construidos con Plotly
- **Barras de conversión**: Comparación visual de todas las variantes
- **Tarjetas detalladas**: Análisis individual de cada comparación
- **Diseño responsive**: Se adapta a cualquier tamaño de pantalla

### 🎯 Métricas Estadísticas
- **Tasas de conversión** con intervalos de confianza
- **Lift relativo** entre variantes
- **P-values** con corrección para múltiples comparaciones
- **Probabilidad Bayesiana** (P2BB)
- **Significancia estadística** con indicadores visuales

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/luciofondon98/ab-testing-analysis-2.0.git
cd ab-testing-analysis-2.0
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Ejecutar la aplicación**
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📖 Cómo Usar

### Formato de Datos

Ingresa los datos en el siguiente formato:

```
Nombre de la Métrica
Variante1 [sesiones] [conversiones]
Variante2 [sesiones] [conversiones]
Variante3 [sesiones] [conversiones]
...
```

### Ejemplo

```
Landing Page Conversion
Control 10000 850
Variant-A 10000 920
Variant-B 10000 780
Variant-C 10000 1050

Email Campaign
Baseline 5000 250
Treatment-1 5000 280
Treatment-2 5000 320
```

### Interpretación de Resultados

#### Matriz de Comparaciones
- 🟢 **Verde**: Mejor rendimiento (diferencia significativa)
- 🔴 **Rojo**: Peor rendimiento (diferencia significativa)
- ⚪ **Gris**: Sin diferencia significativa
- 🔵 **Azul**: Misma variante

#### Métricas Clave
- **Lift**: Mejora porcentual respecto a la variante de comparación
- **P-value**: Significancia estadística (< 0.05 = significativo)
- **P2BB**: Probabilidad de que una variante supere a otra (Bayesiano)
- **Chi-cuadrado**: Test global para múltiples variantes

## 🔧 Tecnologías Utilizadas

- **[Streamlit](https://streamlit.io/)**: Framework de aplicación web
- **[Plotly](https://plotly.com/)**: Visualizaciones interactivas
- **[NumPy](https://numpy.org/)**: Computación numérica
- **[SciPy](https://scipy.org/)**: Análisis estadístico
- **[Pandas](https://pandas.pydata.org/)**: Manipulación de datos

## 📈 Casos de Uso

- **Marketing Digital**: Optimización de campañas publicitarias
- **Product Management**: Testing de nuevas características
- **UX/UI Design**: Validación de cambios de interfaz
- **E-commerce**: Optimización de conversión
- **Email Marketing**: Testing de subject lines y contenido

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Lucio Fondon** - [GitHub](https://github.com/luciofondon98)

## 🙏 Reconocimientos

- Inspirado en las mejores prácticas de análisis A/B testing
- Construido con las mejores herramientas de la comunidad Python
- Diseñado para facilitar la toma de decisiones basada en datos

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub! 