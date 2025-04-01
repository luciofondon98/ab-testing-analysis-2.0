import streamlit as st
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from scipy.stats import beta
from plotly.subplots import make_subplots
import pandas as pd

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

def parse_metrics_data(text):
    """Parse multiple metrics data from text input."""
    metrics_data = {}
    current_metric = None
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a metric name
        if not line.lower().startswith(('baseline', 'treatment')):
            current_metric = line
            metrics_data[current_metric] = {'baseline': None, 'treatment': None}
            continue
            
        # Parse baseline or treatment data
        parts = line.split()
        if len(parts) >= 3:
            group = parts[0].lower()
            if group in ['baseline', 'treatment']:
                metrics_data[current_metric][group] = {
                    'n': int(parts[1]),
                    'x': int(parts[2])
                }
    
    return metrics_data

def calculate_ab_test(control_n, control_x, treatment_n, treatment_x):
    """Calculate A/B test statistics."""
    control_p = control_x / control_n
    treatment_p = treatment_x / treatment_n
    
    # Calculate standard error
    se = np.sqrt(
        (control_p * (1 - control_p) / control_n) +
        (treatment_p * (1 - treatment_p) / treatment_n)
    )
    
    # Calculate z-score
    z_score = (treatment_p - control_p) / se
    
    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    # Calculate relative lift
    relative_lift = ((treatment_p - control_p) / control_p) * 100
    
    return {
        'control_p': control_p,
        'treatment_p': treatment_p,
        'se': se,
        'z_score': z_score,
        'p_value': p_value,
        'relative_lift': relative_lift
    }

def create_metric_plot(metric_name, control_data, treatment_data, results):
    """Create a plot for a single metric."""
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        name='Baseline',
        x=['Baseline'],
        y=[control_data['x']],
        text=[f"{control_data['x']}/{control_data['n']}"],
        textposition='auto',
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name='Treatment',
        x=['Treatment'],
        y=[treatment_data['x']],
        text=[f"{treatment_data['x']}/{treatment_data['n']}"],
        textposition='auto',
        marker_color='#ff7f0e'
    ))
    
    # Update layout
    fig.update_layout(
        title=f"{metric_name} - A/B Test Results",
        yaxis_title='Count',
        showlegend=True,
        height=400
    )
    
    # Add significance annotation
    significance = "Significant" if results['p_value'] < 0.05 else "Not Significant"
    fig.add_annotation(
        text=f"p-value: {results['p_value']:.4f}<br>Lift: {results['relative_lift']:.2f}%<br>{significance}",
        xref='paper',
        yref='paper',
        x=0.02,
        y=0.98,
        showarrow=False,
        font=dict(size=12)
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
    data = st.text_area(
        "Ingresa los datos en el siguiente formato:\n[Nombre de la Métrica]\nBaseline [sesiones] [conversiones]\ntreatment [sesiones] [conversiones]",
        height=200
    )
    
    if st.button("Analizar", type="primary"):
        if data:
            try:
                # Parsear y validar datos
                metrics_data = parse_metrics_data(data)
                
                if not metrics_data:
                    st.error("No valid metrics data found. Please check the format.")
                    return
                
                # Crear pestañas para cada métrica
                tabs = st.tabs(list(metrics_data.keys()))
                
                # Procesar cada métrica
                for tab, (metric_name, data) in zip(tabs, metrics_data.items()):
                    with tab:
                        if data['baseline'] and data['treatment']:
                            # Calcular resultados
                            results = calculate_ab_test(
                                data['baseline']['n'],
                                data['baseline']['x'],
                                data['treatment']['n'],
                                data['treatment']['x']
                            )
                            
                            # Crear y mostrar gráfico
                            fig = create_metric_plot(metric_name, data['baseline'], data['treatment'], results)
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Mostrar resultados detallados
                            st.markdown("### Resultados Detallados")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    "Tasa de Conversión OG",
                                    f"{(data['baseline']['x']/data['baseline']['n'])*100:.2f}%",
                                    f"{data['baseline']['x']}/{data['baseline']['n']}"
                                )
                            
                            with col2:
                                st.metric(
                                    "Tasa de Conversión V1",
                                    f"{(data['treatment']['x']/data['treatment']['n'])*100:.2f}%",
                                    f"{data['treatment']['x']}/{data['treatment']['n']}"
                                )
                            
                            with col3:
                                st.metric(
                                    "Lift Relativo",
                                    f"{results['relative_lift']:.2f}%",
                                    f"p-value: {results['p_value']:.4f}"
                                )
                        else:
                            st.error(f"Missing data for {metric_name}. Please check the format.")
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
        else:
            st.warning("Please enter some data to analyze.")

if __name__ == "__main__":
    main() 