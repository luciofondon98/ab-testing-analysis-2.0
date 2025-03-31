import streamlit as st
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from scipy.stats import beta

# Configuración de la página
st.set_page_config(
    page_title="Análisis A/B Testing",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextArea {
        font-family: monospace;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

def parse_input(text):
    """Parsea el texto de entrada y extrae los datos de la métrica."""
    lines = text.strip().split('\n')
    if len(lines) != 3:
        raise ValueError("El formato debe tener exactamente 3 líneas")
    
    metric_name = lines[0].strip()
    baseline = lines[1].strip().split()
    treatment = lines[2].strip().split()
    
    if len(baseline) != 3 or len(treatment) != 3:
        raise ValueError("Cada línea de datos debe tener 3 elementos")
    
    if baseline[0].lower() != 'baseline' or treatment[0].lower() != 'treatment':
        raise ValueError("Las líneas deben comenzar con 'Baseline' y 'treatment'")
    
    try:
        baseline_sessions = int(baseline[1])
        baseline_conversions = int(baseline[2])
        treatment_sessions = int(treatment[1])
        treatment_conversions = int(treatment[2])
    except ValueError:
        raise ValueError("Los valores numéricos deben ser enteros")
    
    return {
        'metric_name': metric_name,
        'baseline': {'sessions': baseline_sessions, 'conversions': baseline_conversions},
        'treatment': {'sessions': treatment_sessions, 'conversions': treatment_conversions}
    }

def calculate_conversion_rates(data):
    """Calcula las tasas de conversión para ambos grupos."""
    baseline_rate = (data['baseline']['conversions'] / data['baseline']['sessions']) * 100
    treatment_rate = (data['treatment']['conversions'] / data['treatment']['sessions']) * 100
    improvement = ((treatment_rate - baseline_rate) / baseline_rate) * 100
    
    return {
        'baseline_rate': baseline_rate,
        'treatment_rate': treatment_rate,
        'improvement': improvement
    }

def calculate_statistical_significance(data):
    """Calcula la significancia estadística usando chi-square test."""
    contingency_table = np.array([
        [data['baseline']['conversions'], data['baseline']['sessions'] - data['baseline']['conversions']],
        [data['treatment']['conversions'], data['treatment']['sessions'] - data['treatment']['conversions']]
    ])
    
    chi2, p_value = stats.chi2_contingency(contingency_table)[:2]
    return p_value

def calculate_bayesian_probability(data):
    """Calcula la probabilidad bayesiana usando distribución beta."""
    # Parámetros de la distribución beta para cada grupo
    baseline_a = data['baseline']['conversions'] + 1
    baseline_b = data['baseline']['sessions'] - data['baseline']['conversions'] + 1
    treatment_a = data['treatment']['conversions'] + 1
    treatment_b = data['treatment']['sessions'] - data['treatment']['conversions'] + 1
    
    # Simulación Monte Carlo
    n_samples = 10000
    baseline_samples = beta.rvs(baseline_a, baseline_b, size=n_samples)
    treatment_samples = beta.rvs(treatment_a, treatment_b, size=n_samples)
    
    # Probabilidad de que treatment sea mejor que baseline
    p2bb = np.mean(treatment_samples > baseline_samples)
    
    return p2bb

def create_donut_chart(p2bb):
    """Crea un gráfico de dona con las probabilidades P2BB."""
    fig = go.Figure(data=[go.Pie(
        labels=['Treatment', 'Baseline'],
        values=[p2bb * 100, (1 - p2bb) * 100],
        hole=.7,
        marker_colors=['#00CC96', '#EF553B']
    )])
    
    fig.update_layout(
        width=400,
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=[dict(
            text=f'{p2bb*100:.1f}%',
            x=0.5,
            y=0.5,
            font_size=20,
            showarrow=False
        )]
    )
    
    return fig

def main():
    # Título y descripción
    st.title("📊 Análisis A/B Testing")
    st.markdown("""
        Esta aplicación te permite analizar los resultados de pruebas A/B, calculando métricas clave 
        de rendimiento y significancia estadística.
    """)
    
    # Ejemplo de formato
    with st.expander("Ver ejemplo de formato"):
        st.code("""
Website conversion
Baseline 1000 100
treatment 1000 120
        """)
    
    # Área de texto para entrada de datos
    input_text = st.text_area(
        "Ingresa los datos en el siguiente formato:\n[Nombre de la Métrica]\nBaseline [sesiones] [conversiones]\ntreatment [sesiones] [conversiones]",
        height=150
    )
    
    if st.button("Analizar", type="primary"):
        try:
            # Parsear y validar datos
            data = parse_input(input_text)
            
            # Calcular métricas
            conversion_rates = calculate_conversion_rates(data)
            p_value = calculate_statistical_significance(data)
            p2bb = calculate_bayesian_probability(data)
            
            # Mostrar resultados
            st.subheader(f"📈 Resultados para: {data['metric_name']}")
            
            # Métricas en tarjetas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Tasa de conversión OG</div>
                        <div class="metric-value">{conversion_rates['baseline_rate']:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Tasa de conversión V1</div>
                        <div class="metric-value">{conversion_rates['treatment_rate']:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">P-value</div>
                        <div class="metric-value">{p_value:.4f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Mejora/Deterioro</div>
                        <div class="metric-value">{conversion_rates['improvement']:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Gráfico de dona
            st.subheader("🎯 Probabilidad de Mejora")
            st.plotly_chart(create_donut_chart(p2bb), use_container_width=True)
            
            # Interpretación de resultados
            st.subheader("📝 Interpretación")
            if p_value < 0.05:
                st.success("✅ La diferencia es estadísticamente significativa (p < 0.05)")
            else:
                st.warning("⚠️ La diferencia no es estadísticamente significativa (p ≥ 0.05)")
            
            if conversion_rates['improvement'] > 0:
                st.success(f"✅ La variante V1 muestra una mejora del {conversion_rates['improvement']:.2f}%")
            else:
                st.warning(f"⚠️ La variante V1 muestra un deterioro del {abs(conversion_rates['improvement']):.2f}%")
            
        except ValueError as e:
            st.error(f"❌ Error en el formato de entrada: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error al procesar los datos: {str(e)}")

if __name__ == "__main__":
    main() 