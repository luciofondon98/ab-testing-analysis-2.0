import streamlit as st
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from scipy.stats import beta, chi2_contingency
from plotly.subplots import make_subplots
import pandas as pd
from itertools import combinations
import base64
import json
import urllib.parse

# Configuración de la página
st.set_page_config(
    page_title="Análisis A/B/N Testing",
    page_icon="📊",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stApp {
        background-color: #1B365D;
    }
    .main {
        padding: 2rem;
    }
    .stTextArea {
        font-family: monospace;
    }
    div[data-testid="stMarkdownContainer"] {
        color: white;
    }
    .stTextArea > label {
        color: white !important;
    }
    button[data-testid="baseButton-secondary"] {
        background-color: #3CCFE7;
        color: #1B365D;
    }
    .stExpander {
        border-color: #3CCFE7;
    }
    .stExpander > details > summary {
        color: white;
    }
    .stExpander > details > div {
        color: white;
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
    .st-emotion-cache-10trblm.e1nzilvr1 {
        color: white !important;
    }
    .multivariant-card {
        width: 100%;
        background: #4A6489;
        box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
        border-radius: 12px;
        margin: 20px auto;
        color: white;
        position: relative;
        overflow: hidden;
        padding: 20px;
    }
    .variant-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #3CCFE7;
    }
    .variant-name {
        font-weight: bold;
        min-width: 120px;
    }
    .variant-metric {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .metric-box {
        background: #FFFFFF;
        color: #1B365D;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        min-width: 80px;
        text-align: center;
    }
    .share-url-box {
        background: #4A6489;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
        border: 2px solid #3CCFE7;
    }
    .share-url-input {
        width: 100%;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #3CCFE7;
        background: #1B365D;
        color: white;
        font-family: monospace;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

def encode_data_to_url(data):
    """Encode data to URL-safe base64 string."""
    try:
        json_str = json.dumps(data)
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        return encoded
    except Exception:
        return None

def decode_data_from_url(encoded_data):
    """Decode data from URL-safe base64 string."""
    try:
        decoded = base64.urlsafe_b64decode(encoded_data.encode()).decode()
        return json.loads(decoded)
    except Exception:
        return None

def get_browser_url():
    """Get current URL from browser using JavaScript."""
    import streamlit.components.v1 as components
    
    # Create a hidden component that gets the current URL
    browser_url = components.html(
        """
        <script>
        // Get the current URL and send it to Streamlit
        const currentUrl = window.location.href.split('?')[0];
        window.parent.postMessage({
            type: 'streamlit:browserUrl',
            url: currentUrl
        }, '*');
        </script>
        <div style="display: none;">Getting URL...</div>
        """,
        height=0
    )
    return None  # This approach needs session state to work

def generate_share_url(data):
    """Generate shareable URL with data."""
    encoded = encode_data_to_url(data)
    if encoded:
        # Strategy: Use a simple but effective detection
        server_address = st.get_option("browser.serverAddress")
        port = st.get_option("server.port") or 8501
        
        # If serverAddress is localhost but we're actually on Streamlit Cloud,
        # we need to detect this differently
        if server_address == "localhost":
            # Try to detect if we're on Streamlit Cloud by checking environment
            import os
            
            # Check various environment variables that might indicate Streamlit Cloud
            env_vars = [
                'STREAMLIT_SERVER_HEADLESS',
                'STREAMLIT_SHARING_MODE', 
                'HOSTNAME',
                'DYNO',  # Heroku
                'RENDER_SERVICE_NAME',  # Render
            ]
            
            is_cloud = any(
                var in os.environ and 'streamlit' in str(os.environ.get(var, '')).lower()
                for var in env_vars
            )
            
            # Additional check: if we have specific cloud indicators
            if not is_cloud:
                is_cloud = (
                    os.environ.get('STREAMLIT_SERVER_HEADLESS') == 'true' or
                    'RENDER' in os.environ or
                    'DYNO' in os.environ
                )
            
            if is_cloud:
                # We're on a cloud platform but serverAddress is still localhost
                # Create a placeholder that the user can easily replace
                share_url = f"https://YOUR-STREAMLIT-APP-URL.streamlit.app/?data={encoded}"
            else:
                # Actually localhost
                share_url = f"http://localhost:{port}/?data={encoded}"
        else:
            # serverAddress is not localhost, use it
            if server_address.startswith("http"):
                base_url = server_address.rstrip('/')
            else:
                base_url = f"https://{server_address}"
            share_url = f"{base_url}/?data={encoded}"
        
        return share_url
    return None

def parse_metrics_data(text):
    """Parse multiple metrics data from text input supporting both legacy and N variants."""
    metrics_data = {}
    current_metric = None
    
    for line in text.strip().split('\n'):
        # Si la línea está vacía, continuar
        if not line.strip():
            continue
            
        # Dividir por tabulaciones si hay, si no, buscar el último espacio antes de los números
        if '\t' in line:
            parts = line.split('\t')
        else:
            # Encontrar la posición del primer número
            line_parts = line.strip().split()
            for i, part in enumerate(line_parts):
                if part.replace('.', '').replace(',', '').isdigit():
                    # Unir todo lo anterior como el nombre
                    name = ' '.join(line_parts[:i])
                    # Y tomar los números como el resto
                    numbers = line_parts[i:]
                    parts = [name] + numbers
                    break
            else:
                # Si no hay números, es un nombre de métrica
                current_metric = line.strip()
                metrics_data[current_metric] = {'variants': []}
                continue
            
        # Si tenemos 3 o más partes (nombre y números)
        if len(parts) >= 3:
            try:
                variant_name = parts[0].strip()
                n = int(parts[1].strip().replace(',', ''))  # sesiones
                x = int(parts[2].strip().replace(',', ''))  # conversiones
                
                if n < x:
                    raise ValueError(f"El número de conversiones ({x}) no puede ser mayor que el número de sesiones ({n}) en: {line}")
                
                if current_metric:
                    metrics_data[current_metric]['variants'].append({
                        'name': variant_name,
                        'n': n,
                        'x': x
                    })
                
            except ValueError as e:
                if "El número de conversiones" in str(e):
                    raise e
                raise ValueError(f"Los valores deben ser números enteros en la línea: {line}")
    
    # Validar que cada métrica tenga al menos 2 variantes
    for metric, data in metrics_data.items():
        if len(data['variants']) < 2:
            raise ValueError(f"La métrica {metric} debe tener al menos 2 variantes")
    
    # Mantener compatibilidad con formato legacy para 2 variantes
    for metric, data in metrics_data.items():
        if len(data['variants']) == 2:
            data['baseline'] = data['variants'][0]
            data['treatment'] = data['variants'][1]
            
    return metrics_data

def calculate_ab_test(control_n, control_x, treatment_n, treatment_x):
    """Calculate A/B test statistics for legacy support."""
    control_p = control_x / control_n
    treatment_p = treatment_x / treatment_n
    
    # Calculate standard error
    se = np.sqrt(
        (control_p * (1 - control_p) / control_n) +
        (treatment_p * (1 - treatment_p) / treatment_n)
    )
    
    # Calculate z-score
    z_score = (treatment_p - control_p) / se if se > 0 else 0
    
    # Calculate p-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score))) if se > 0 else 1
    
    # Calculate relative lift
    relative_lift = ((treatment_p - control_p) / control_p) * 100 if control_p > 0 else 0
    
    # Calculate bayesian probability
    n_simulations = 10000
    baseline_posterior = np.random.beta(control_x + 1, control_n - control_x + 1, n_simulations)
    treatment_posterior = np.random.beta(treatment_x + 1, treatment_n - treatment_x + 1, n_simulations)
    p2bb = np.mean(treatment_posterior > baseline_posterior)
    
    return {
        'control_p': control_p,
        'treatment_p': treatment_p,
        'se': se,
        'z_score': z_score,
        'p_value': p_value,
        'relative_lift': relative_lift,
        'p2bb': p2bb
    }

def calculate_chi_square_test(variants):
    """Calculate Chi-square test for multiple variants."""
    # Crear tabla de contingencia
    conversions = [variant['x'] for variant in variants]
    non_conversions = [variant['n'] - variant['x'] for variant in variants]
    
    # Tabla de contingencia: [conversiones, no_conversiones] para cada variante
    contingency_table = np.array([conversions, non_conversions])
    
    # Test Chi-cuadrado
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return {
        'chi2': chi2,
        'p_value': p_value,
        'dof': dof,
        'significant': p_value < 0.05
    }

def calculate_pairwise_comparisons(variants):
    """Calculate pairwise comparisons between all variants."""
    comparisons = []
    
    # Comparaciones vs control (primera variante)
    control = variants[0]
    for i, variant in enumerate(variants[1:], 1):
        comparison = calculate_single_comparison(control, variant, is_control_comparison=True)
        comparisons.append(comparison)
    
    return comparisons

def calculate_all_pairwise_comparisons(variants):
    """Calculate all possible pairwise comparisons between variants."""
    all_comparisons = []
    
    # Generar todas las combinaciones posibles de variantes
    for i in range(len(variants)):
        for j in range(i + 1, len(variants)):
            variant_a = variants[i]
            variant_b = variants[j]
            
            comparison = calculate_single_comparison(variant_a, variant_b, is_control_comparison=(i == 0))
            all_comparisons.append(comparison)
    
    return all_comparisons

def calculate_single_comparison(variant_a, variant_b, is_control_comparison=False):
    """Calculate statistics for a single pairwise comparison."""
    a_p = variant_a['x'] / variant_a['n']
    b_p = variant_b['x'] / variant_b['n']
    
    # Calculate standard error
    se = np.sqrt(
        (a_p * (1 - a_p) / variant_a['n']) +
        (b_p * (1 - b_p) / variant_b['n'])
    )
    
    # Calculate z-score
    if se > 0:
        z_score = (b_p - a_p) / se
        # Calculate p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    else:
        z_score = 0
        p_value = 1
    
    # Calculate relative lift
    if a_p > 0:
        relative_lift = ((b_p - a_p) / a_p) * 100
    else:
        relative_lift = 0
    
    # Calculate bayesian probability
    n_simulations = 10000
    a_posterior = np.random.beta(variant_a['x'] + 1, variant_a['n'] - variant_a['x'] + 1, n_simulations)
    b_posterior = np.random.beta(variant_b['x'] + 1, variant_b['n'] - variant_b['x'] + 1, n_simulations)
    p2bb = np.mean(b_posterior > a_posterior)
    
    return {
        'variant_a_name': variant_a['name'],
        'variant_b_name': variant_b['name'],
        'variant_a_p': a_p,
        'variant_b_p': b_p,
        'relative_lift': relative_lift,
        'p_value': p_value,
        'p2bb': p2bb,
        'significant': p_value < 0.05,
        'is_control_comparison': is_control_comparison
    }

def create_metric_card(metric_name, data, results):
    """Create a styled card for a metric (legacy format)."""
    st.markdown("""
        <style>
        .metric-card {
            width: 600px;
            height: 220px;
            background: #4A6489;
            box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            margin: 20px auto;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .metric-card:hover {
            transform: scale(1.01);
        }
        .metric-card:active {
            transform: scale(0.99);
        }
        .metric-header {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            padding: 16px;
            gap: 10px;
            width: 100%;
            height: 54px;
            background: #FFFFFF;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .metric-header-emoji {
            font-size: 24px;
            line-height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 8px;
        }
        .metric-header-text {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 900;
            font-size: 20px;
            line-height: 24px;
            color: #1B365D;
            display: flex;
            align-items: center;
        }
        .metric-content {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            padding: 0 20px;
            gap: 20px;
            height: 120px;
        }
        .metric-section {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .metric-label {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #FFFFFF;
            margin-bottom: 4px;
            text-align: left;
        }
        .conversion-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .conversion-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .conversion-label {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #FFFFFF;
            width: 30px;
        }
        .metric-value {
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 6px 12px;
            min-width: 80px;
            height: 34px;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #1B365D;
        }
        .metric-improvement {
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 6px 12px;
            min-width: 100px;
            height: 34px;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #69BE28;
        }
        .p2bb-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 0;
            width: 100%;
            margin-top: 0;
        }
        .p2bb-chart {
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 0px;
            align-items: center;
        }
        .p2bb-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: auto;
        }
        .bar-container {
            width: 94px;
            height: 34px;
            background: #FFFFFF;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
            background: #3CCFE7;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .bar-value {
            font-family: 'Clan OT', sans-serif;
            font-weight: 700;
            font-size: 14px;
            position: absolute;
            width: 100%;
            text-align: center;
            z-index: 1;
        }
        </style>
    """, unsafe_allow_html=True)

    # Determinar los porcentajes y redondearlos
    v1_percentage = round(results['p2bb'] * 100)
    og_percentage = round((1 - results['p2bb']) * 100)
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-header">
                <span class="metric-header-emoji">🎯</span>
                <span class="metric-header-text">{metric_name}</span>
            </div>
            <div class="metric-content">
                <div class="metric-section">
                    <div class="metric-label">Conversion</div>
                    <div class="conversion-container">
                        <div class="conversion-row">
                            <span class="conversion-label">OG</span>
                            <div class="metric-value">{results['control_p']*100:.1f}%</div>
                        </div>
                        <div class="conversion-row">
                            <span class="conversion-label">V1</span>
                            <div class="metric-value">{results['treatment_p']*100:.1f}%</div>
                        </div>
                    </div>
                </div>
                <div class="metric-section p2bb-section">
                    <div class="metric-label">P2BB</div>
                    <div class="p2bb-chart">
                        <div class="p2bb-bar">
                            <div class="bar-container">
                                <div class="bar-fill" style="width: {og_percentage}%"></div>
                                <span class="bar-value" style="color: {('#FFFFFF' if og_percentage > 50 else '#3CCFE7')}">{og_percentage}%</span>
                            </div>
                        </div>
                        <div class="p2bb-bar">
                            <div class="bar-container">
                                <div class="bar-fill" style="width: {v1_percentage}%"></div>
                                <span class="bar-value" style="color: {('#FFFFFF' if v1_percentage > 50 else '#3CCFE7')}">{v1_percentage}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="metric-section">
                    <div class="metric-label">Improvement</div>
                    <div class="metric-improvement" style="color: {'#69BE28' if results['relative_lift'] > 0 else '#FF0000'}">
                        {'+' if results['relative_lift'] > 0 else ''}{results['relative_lift']:.2f}%
                    </div>
                </div>
                <div class="metric-section">
                    <div class="metric-label">P-value</div>
                    <div class="metric-value">{results['p_value']:.3f}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_multivariant_summary_card(metric_name, variants, chi_square_result):
    """Create a summary card for multivariant test."""
    
    st.markdown(f"""
        <div class="multivariant-card">
            <h3>🎯 {metric_name} - Resumen General</h3>
            <div style="margin: 20px 0;">
                <strong>Test Chi-cuadrado:</strong> 
                <span style="color: {'#69BE28' if chi_square_result['significant'] else '#FF6B6B'}">
                    {'Significativo' if chi_square_result['significant'] else 'No significativo'}
                </span>
                (p-value: {chi_square_result['p_value']:.4f})
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
    """, unsafe_allow_html=True)
    
    for variant in variants:
        conversion_rate = (variant['x'] / variant['n']) * 100
        st.markdown(f"""
            <div class="variant-row">
                <div class="variant-name">{variant['name']}</div>
                <div class="variant-metric">
                    <div class="metric-box">{conversion_rate:.2f}%</div>
                    <div class="metric-box">{variant['x']:,}/{variant['n']:,}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def create_comparison_matrix(metric_name, variants):
    """Create an interactive matrix showing all pairwise comparison results with hover tooltips."""
    st.markdown(f"### 📋 Matriz de Comparaciones - {metric_name}")
    
    # Crear datos para la matriz
    n_variants = len(variants)
    variant_names = [v['name'] for v in variants]
    
    # Inicializar matrices
    z_values = []  # Para colores
    hover_texts = []  # Para tooltips
    display_texts = []  # Para texto mostrado
    
    for i in range(n_variants):
        z_row = []
        hover_row = []
        display_row = []
        
        for j in range(n_variants):
            if i == j:
                # Diagonal - misma variante
                conversion_rate = (variants[i]['x'] / variants[i]['n']) * 100
                z_row.append(0)  # Valor neutral para color
                hover_row.append(f"{variants[i]['name']}<br>Conversión: {conversion_rate:.2f}%<br>Datos: {variants[i]['x']:,}/{variants[i]['n']:,}")
                display_row.append("—")
            else:
                # Comparación entre variantes
                variant_a = variants[i]
                variant_b = variants[j]
                comparison = calculate_single_comparison(variant_a, variant_b)
                
                # Texto del tooltip
                hover_text = f"""
{variant_a['name']} vs {variant_b['name']}<br>
• {variant_a['name']}: {comparison['variant_a_p']*100:.2f}% ({variant_a['x']:,}/{variant_a['n']:,})<br>
• {variant_b['name']}: {comparison['variant_b_p']*100:.2f}% ({variant_b['x']:,}/{variant_b['n']:,})<br>
• Lift: {'+' if comparison['relative_lift'] > 0 else ''}{comparison['relative_lift']:.2f}%<br>
• P-value: {comparison['p_value']:.4f}<br>
• P2BB: {comparison['p2bb']*100:.1f}%<br>
• Significativo: {'Sí' if comparison['significant'] else 'No'}
                """.strip()
                
                hover_row.append(hover_text)
                
                # Determinar valor y color
                if comparison['significant']:
                    if comparison['relative_lift'] > 0:
                        z_row.append(1)  # Verde (ganador)
                        display_row.append(f"+{comparison['relative_lift']:.1f}%")
                    else:
                        z_row.append(-1)  # Rojo (perdedor)
                        display_row.append(f"{comparison['relative_lift']:.1f}%")
                else:
                    z_row.append(0.5)  # Gris (neutral)
                    display_row.append("≈")
        
        z_values.append(z_row)
        hover_texts.append(hover_row)
        display_texts.append(display_row)
    
    # Crear el heatmap con plotly
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=variant_names,
        y=variant_names,
        text=display_texts,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts,
        colorscale=[
            [0.0, '#C62828'],    # Rojo para perdedor
            [0.25, '#757575'],   # Gris para neutral
            [0.5, '#6A7BAA'],    # Azul para diagonal
            [0.75, '#757575'],   # Gris para neutral
            [1.0, '#2E7D32']     # Verde para ganador
        ],
        showscale=False,
        xgap=2,
        ygap=2
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=max(400, n_variants * 60),  # Altura dinámica
        margin=dict(l=50, r=50, t=30, b=30),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(n_variants)),
            ticktext=variant_names,
            side='top'
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(n_variants)),
            ticktext=variant_names,
            autorange='reversed'  # Para que coincida con la lógica de matriz
        )
    )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Leyenda mejorada
    st.markdown("""
    <div style="background: #4A6489; border-radius: 8px; padding: 15px; margin-top: 10px;">
        <div style="display: flex; gap: 20px; flex-wrap: wrap; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #2E7D32; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Mejor rendimiento</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #C62828; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Peor rendimiento</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #757575; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Sin diferencia significativa</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #6A7BAA; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Misma variante</span>
            </div>
        </div>
        <div style="margin-top: 10px; text-align: center; font-style: italic; color: #E0E0E0; font-size: 0.8em;">
            💡 Pasa el cursor sobre cualquier celda para ver detalles completos de la comparación
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_all_comparisons_section(metric_name, all_comparisons):
    """Create section showing all possible pairwise comparisons."""
    # Separar comparaciones vs control de comparaciones entre variantes
    control_comparisons = [comp for comp in all_comparisons if comp['is_control_comparison']]
    variant_comparisons = [comp for comp in all_comparisons if not comp['is_control_comparison']]
    
    # Mostrar comparaciones vs control
    if control_comparisons:
        st.markdown(f"### 📊 Comparaciones vs Control")
        create_comparison_cards(control_comparisons, is_control_section=True)
    
    # Mostrar comparaciones entre variantes
    if variant_comparisons:
        st.markdown(f"### 🔄 Comparaciones entre Variantes")
        create_comparison_cards(variant_comparisons, is_control_section=False)

def create_comparison_cards(comparisons, is_control_section=True):
    """Create comparison cards with improved styling and visible p-values."""
    for comparison in comparisons:
        # Determinar colores y títulos según el tipo de comparación
        if is_control_section:
            card_color = "#4A6489"
            icon = "📈"
        else:
            card_color = "#5A7099"
            icon = "⚖️"
        
        st.markdown(f"""
            <div class="multivariant-card" style="background: {card_color}; padding: 15px; margin: 10px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span style="font-size: 1.2em; margin-right: 10px;">{icon}</span>
                    <h4 style="margin: 0;">{comparison['variant_a_name']} vs {comparison['variant_b_name']}</h4>
                </div>
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px;">
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">{comparison['variant_a_name']}</div>
                        <div class="metric-box">{comparison['variant_a_p']*100:.2f}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">{comparison['variant_b_name']}</div>
                        <div class="metric-box">{comparison['variant_b_p']*100:.2f}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">Lift Relativo</div>
                        <div class="metric-box" style="background: {'#E8F5E8' if comparison['relative_lift'] > 0 else '#FFE8E8'}; color: {'#2E7D32' if comparison['relative_lift'] > 0 else '#C62828'};">
                            {'+' if comparison['relative_lift'] > 0 else ''}{comparison['relative_lift']:.2f}%
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">P-value</div>
                        <div class="metric-box" style="background: {'#E8F5E8' if comparison['significant'] else '#FFE8E8'}; color: {'#2E7D32' if comparison['significant'] else '#C62828'};">
                            {comparison['p_value']:.4f}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">P2BB</div>
                        <div class="metric-box" style="background: {'#E3F2FD' if comparison['p2bb'] > 0.5 else '#FFF3E0'}; color: {'#1565C0' if comparison['p2bb'] > 0.5 else '#E65100'};">
                            {comparison['p2bb']*100:.1f}%
                        </div>
                    </div>
                </div>
                <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <div style="text-align: center;">
                        <div style="padding: 8px 20px; border-radius: 20px; background: {'#2E7D32' if comparison['significant'] else '#C62828'}; color: white; font-size: 0.9em; display: inline-block;">
                            {'✓ Significativo' if comparison['significant'] else '✗ No significativo'} (α = 0.05)
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

def create_visualization(metric_name, variants):
    """Create visualization for multivariant test."""
    # Crear gráfico de barras con conversiones
    variant_names = [v['name'] for v in variants]
    conversion_rates = [(v['x'] / v['n']) * 100 for v in variants]
    
    fig = go.Figure()
    
    # Colores diferentes para cada variante
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    
    fig.add_trace(go.Bar(
        x=variant_names,
        y=conversion_rates,
        marker_color=colors[:len(variants)],
        text=[f'{rate:.2f}%' for rate in conversion_rates],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=f'Tasas de Conversión - {metric_name}',
        xaxis_title='Variantes',
        yaxis_title='Tasa de Conversión (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def convert_metrics_to_text(metrics):
    """Convert metrics data back to text format for sharing."""
    text_lines = []
    for metric_name, data in metrics.items():
        text_lines.append(metric_name)
        for variant in data['variants']:
            text_lines.append(f"{variant['name']} {variant['n']} {variant['x']}")
        text_lines.append("")  # Empty line between metrics
    return "\n".join(text_lines)

def create_share_url_section(metrics):
    """Create section for sharing URL with current data."""
    if metrics:
        st.markdown("#### 🔗 Compartir")
        
        # Generar URL compartible
        share_url = generate_share_url(metrics)
        
        if share_url:
            # Si la URL contiene el placeholder, mostrar ayuda especial
            if "YOUR-STREAMLIT-APP-URL" in share_url:
                st.warning("⚠️ Reemplaza YOUR-STREAMLIT-APP-URL con tu URL real de Streamlit")
                
                # Mostrar campo editable para que el usuario pueda corregir
                corrected_url = st.text_input(
                    "Corrige la URL:",
                    value=share_url,
                    help="Reemplaza YOUR-STREAMLIT-APP-URL con tu URL real (ej: ab-testing-analysis-20-excagd7wmh3lhplwa4hqvb.streamlit.app)"
                )
                
                if corrected_url != share_url and "YOUR-STREAMLIT-APP-URL" not in corrected_url:
                    st.success("✅ URL corregida!")
            else:
                # Mostrar URL en un input copiable más compacto
                st.text_input(
                    "URL:",
                    value=share_url,
                    help="Selecciona todo el texto y copia con Ctrl+C para compartir",
                    label_visibility="collapsed"
                )
            
            # Texto de ayuda más pequeño
            st.caption("💡 Selecciona el texto de arriba y copia con Ctrl+C")
            
            # Debug info (opcional - comentar en producción)
            import os
            env_debug = {}
            interesting_vars = ['HOSTNAME', 'STREAMLIT_SERVER_HEADLESS', 'RENDER_SERVICE_NAME', 'DYNO', 'STREAMLIT_SHARING_MODE']
            for var in interesting_vars:
                if var in os.environ:
                    env_debug[var] = os.environ[var]
            
            debug_info = f"""
            Debug: 
            - serverAddress='{st.get_option("browser.serverAddress")}' 
            - port={st.get_option("server.port")}
            - Environment vars: {env_debug}
            """
            if st.checkbox("🐛 Debug info", value=False):
                st.code(debug_info)
            
        else:
            st.warning("Error generando URL")

def load_data_from_url():
    """Load data from URL parameter if present."""
    try:
        # Usar la nueva API de query params
        if 'data' in st.query_params:
            encoded_data = st.query_params['data']
            
            decoded_data = decode_data_from_url(encoded_data)
            
            if decoded_data:
                # Convert back to text format
                loaded_text = convert_metrics_to_text(decoded_data)
                return loaded_text, decoded_data
            else:
                # Solo mostrar error si hay problema real
                st.error("❌ No se pudo decodificar los datos de la URL")
    except Exception as e:
        # Mostrar error en caso de falla
        st.error(f"❌ Error cargando datos de URL: {str(e)}")
    
    return None, None

def main():
    st.markdown("""
        <style>
        .stApp {
            background-color: #1B365D;
        }
        .main {
            padding: 2rem;
        }
        .stTextArea {
            font-family: monospace;
        }
        div[data-testid="stMarkdownContainer"] {
            color: white;
        }
        .stTextArea > label {
            color: white !important;
        }
        button[data-testid="baseButton-secondary"] {
            background-color: #3CCFE7;
            color: #1B365D;
        }
        .stExpander {
            border-color: #3CCFE7;
        }
        .stExpander > details > summary {
            color: white;
        }
        .stExpander > details > div {
            color: white;
        }
        .st-emotion-cache-10trblm.e1nzilvr1 {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Intentar cargar datos de URL
    loaded_text, loaded_metrics = load_data_from_url()
    
    if loaded_text:
        st.success("✅ Datos cargados desde URL compartida y analizados automáticamente!")

    # Header section - título y descripción
    st.title("📊 Análisis A/B/N Testing")
    st.write("Esta aplicación te permite analizar los resultados de pruebas A/B/N con múltiples variantes, calculando métricas clave de rendimiento y significancia estadística.")

    # Crear sección de input en dos columnas  
    col_input_left, col_input_right = st.columns([3, 1])

    # Columna de input de datos (izquierda)
    with col_input_left:
        st.subheader("📝 Datos de Entrada")
        
        with st.expander("Ver ejemplo de formato", expanded=False):
            st.code("""NSR Flights
Control 1000 100
Variant-A 1000 120
Variant-B 1000 90
Variant-C 1000 140

Website conversion
Baseline 2000 200
Treatment-1 2000 220
Treatment-2 2000 180
Treatment-3 2000 250""")
        
        # Área de texto para input (usar datos cargados si existen)
        default_data = loaded_text if loaded_text else ""
        data = st.text_area(
            "Formato: [Nombre Métrica] → [Nombre Variante] [sesiones] [conversiones]",
            height=300,
            value=default_data,
            placeholder="""NSR Flights
Control 1000 100
Variant-A 1000 120
Variant-B 1000 90
Variant-C 1000 140

Website conversion
Baseline 2000 200
Treatment-1 2000 220"""
        )
        
        # Cambiar texto del botón si hay datos cargados desde URL
        button_text = "Re-analizar" if loaded_text else "Analizar"
        
        if st.button(button_text, type="primary"):
            if data:
                try:
                    metrics = parse_metrics_data(data)
                    st.session_state.metrics = metrics
                    st.session_state.show_results = True
                    st.session_state.auto_loaded = False  # Marcar como análisis manual
                except Exception as e:
                    st.error(f"Error al procesar los datos: {str(e)}")
            else:
                st.warning("Por favor, ingresa algunos datos para analizar.")

    # Columna derecha - Compartir (solo si hay resultados)
    with col_input_right:
        if 'show_results' in st.session_state and st.session_state.show_results:
            metrics = st.session_state.metrics
            # Sección para compartir URL
            create_share_url_section(metrics)

    # Auto-cargar y auto-analizar si hay datos de URL
    if loaded_metrics:
        st.session_state.metrics = loaded_metrics
        st.session_state.show_results = True
        st.session_state.auto_loaded = True

    # Sección de resultados - ancho completo
    if 'show_results' in st.session_state and st.session_state.show_results:
        st.markdown("---")
        st.header("📊 Resultados del Análisis")
        
        metrics = st.session_state.metrics
        
        # Procesar cada métrica
        for metric_name, data in metrics.items():
            # Verificar si tiene la estructura de variantes nueva o la legacy
            if 'variants' in data and len(data['variants']) > 0:
                variants = data['variants']
                
                # Contenedor para cada métrica
                st.subheader(f"🎯 {metric_name}")
                
                # Si solo hay 2 variantes, usar el formato original (más compacto)
                if len(variants) == 2 and 'baseline' in data and 'treatment' in data:
                    results = calculate_ab_test(
                        data['baseline']['n'], data['baseline']['x'],
                        data['treatment']['n'], data['treatment']['x']
                    )
                    
                    # Mostrar en dos columnas: card + gráfico
                    col_card, col_chart = st.columns([1, 1])
                    with col_card:
                        create_metric_card(metric_name, data, results)
                    
                else:
                    # Análisis multivariante - Layout mejorado
                    chi_square_result = calculate_chi_square_test(variants)
                    
                    # Resumen general en la parte superior
                    create_multivariant_summary_card(metric_name, variants, chi_square_result)
                    
                    # Dos columnas para matriz y gráfico
                    col_matrix, col_chart = st.columns([1, 1])
                    
                    with col_matrix:
                        create_comparison_matrix(metric_name, variants)
                    
                    with col_chart:
                        fig = create_visualization(metric_name, variants)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparaciones detalladas en ancho completo (colapsadas por defecto)
                    with st.expander(f"Ver comparaciones detalladas - {metric_name}", expanded=False):
                        all_comparisons = calculate_all_pairwise_comparisons(variants)
                        create_all_comparisons_section(metric_name, all_comparisons)
            
            st.markdown("---")

if __name__ == "__main__":
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    main() 