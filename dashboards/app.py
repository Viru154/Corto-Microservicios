import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from prophet import Prophet
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from config import query_to_df
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard Cine - Análisis con IA", layout="wide")

# Título principal
st.title("🎬 Sistema de Cines Distribuido - Dashboard Analítico con IA")
st.markdown("---")

# Sidebar
st.sidebar.header("Navegación")
dashboard = st.sidebar.radio(
    "Selecciona un dashboard:",
    ["📊 Resumen General", "📈 Predicción de Ventas (IA)", "🎯 Clustering de Películas (IA)", "⚠️ Detección de Anomalías (IA)"]
)

# ============================================
# DASHBOARD 1: RESUMEN GENERAL
# ============================================
if dashboard == "📊 Resumen General":
    st.header("Resumen General del Negocio")
    
    # Métricas por país
    query_pais = """
    SELECT 
        p.nombre as pais,
        SUM(fv.cantidad_boletos) as total_boletos,
        SUM(fv.ingreso_total) as total_ingresos,
        COUNT(DISTINCT fv.pelicula_id) as peliculas_distintas
    FROM fact_ventas fv
    JOIN dim_pais p ON fv.pais_id = p.pais_id
    GROUP BY p.nombre
    """
    df_pais = query_to_df(query_pais)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Boletos Vendidos", f"{df_pais['total_boletos'].sum():,.0f}")
        st.metric("Guatemala", f"{df_pais[df_pais['pais']=='Guatemala']['total_boletos'].values[0]:,.0f}")
    
    with col2:
        st.metric("Ingresos Totales", f"${df_pais['total_ingresos'].sum():,.2f}")
        st.metric("El Salvador", f"{df_pais[df_pais['pais']=='El Salvador']['total_boletos'].values[0]:,.0f}")
    
    # Gráfico de barras por país
    fig_pais = px.bar(df_pais, x='pais', y='total_ingresos', 
                      title='Ingresos por País',
                      labels={'total_ingresos': 'Ingresos', 'pais': 'País'},
                      color='pais')
    st.plotly_chart(fig_pais, use_container_width=True)
    
    # Top 10 películas
    query_top = """
    SELECT 
        p.titulo,
        SUM(fv.cantidad_boletos) as boletos,
        SUM(fv.ingreso_total) as ingresos
    FROM fact_ventas fv
    JOIN dim_pelicula p ON fv.pelicula_id = p.pelicula_id
    GROUP BY p.titulo
    ORDER BY ingresos DESC
    LIMIT 10
    """
    df_top = query_to_df(query_top)
    
    st.subheader("Top 10 Películas por Ingresos")
    fig_top = px.bar(df_top, x='titulo', y='ingresos', 
                     labels={'ingresos': 'Ingresos ($)', 'titulo': 'Película'},
                     color='ingresos')
    fig_top.update_xaxes(tickangle=45)
    st.plotly_chart(fig_top, use_container_width=True)

# ============================================
# DASHBOARD 2: PREDICCIÓN CON IA (PROPHET)
# ============================================
elif dashboard == "📈 Predicción de Ventas (IA)":
    st.header("Predicción de Ventas con Prophet (Facebook AI)")
    st.info("📌 Utilizando Prophet - Modelo de series temporales desarrollado por Facebook")
    
    # Extraer datos históricos
    query_historico = """
    SELECT 
        t.fecha as ds,
        SUM(fv.ingreso_total) as y
    FROM fact_ventas fv
    JOIN dim_tiempo t ON fv.tiempo_id = t.tiempo_id
    GROUP BY t.fecha
    ORDER BY t.fecha
    """
    df_historico = query_to_df(query_historico)
    
    st.subheader("Datos Históricos")
    st.write(f"Registros: {len(df_historico):,} días")
    
    # Entrenar modelo Prophet
    with st.spinner('Entrenando modelo de IA...'):
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        model.fit(df_historico)
        
        # Predicción a 90 días
        future = model.make_future_dataframe(periods=90)
        forecast = model.predict(future)
    
    # Visualización
    st.subheader("Predicción de Ingresos - Próximos 90 Días")
    
    fig = go.Figure()
    
    # Datos históricos
    fig.add_trace(go.Scatter(
        x=df_historico['ds'],
        y=df_historico['y'],
        mode='lines',
        name='Histórico',
        line=dict(color='blue')
    ))
    
    # Predicción
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Predicción',
        line=dict(color='red', dash='dash')
    ))
    
    # Intervalo de confianza
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        fill=None,
        mode='lines',
        line=dict(color='rgba(255,0,0,0)'),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgba(255,0,0,0)'),
        name='Intervalo de confianza'
    ))
    
    fig.update_layout(
        title='Predicción de Ingresos Diarios',
        xaxis_title='Fecha',
        yaxis_title='Ingresos ($)',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas de predicción
    col1, col2, col3 = st.columns(3)
    prediccion_30d = forecast.tail(30)['yhat'].sum()
    prediccion_60d = forecast.tail(60)['yhat'].sum()
    prediccion_90d = forecast.tail(90)['yhat'].sum()
    
    col1.metric("Predicción 30 días", f"${prediccion_30d:,.2f}")
    col2.metric("Predicción 60 días", f"${prediccion_60d:,.2f}")
    col3.metric("Predicción 90 días", f"${prediccion_90d:,.2f}")

# ============================================
# DASHBOARD 3: CLUSTERING (K-MEANS)
# ============================================
elif dashboard == "🎯 Clustering de Películas (IA)":
    st.header("Segmentación de Películas con K-Means")
    st.info("📌 Utilizando K-Means Clustering - Algoritmo de aprendizaje no supervisado")
    
    # Extraer features de películas
    query_features = """
    SELECT 
        p.pelicula_id,
        p.titulo,
        p.genero,
        SUM(fv.cantidad_boletos) as total_boletos,
        SUM(fv.ingreso_total) as total_ingresos,
        AVG(fv.precio_promedio) as precio_promedio,
        COUNT(DISTINCT fv.tiempo_id) as dias_proyeccion
    FROM fact_ventas fv
    JOIN dim_pelicula p ON fv.pelicula_id = p.pelicula_id
    GROUP BY p.pelicula_id, p.titulo, p.genero
    HAVING SUM(fv.cantidad_boletos) > 100
    """
    df_features = query_to_df(query_features)
    
    st.write(f"Analizando {len(df_features)} películas")
    
    # Preparar datos para clustering
    features = df_features[['total_boletos', 'total_ingresos', 'precio_promedio', 'dias_proyeccion']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # K-Means
    n_clusters = st.slider("Número de clusters", 2, 6, 4)
    
    with st.spinner('Ejecutando algoritmo K-Means...'):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_features['cluster'] = kmeans.fit_predict(features_scaled)
    
    # Visualización 3D
    fig = px.scatter_3d(
        df_features,
        x='total_boletos',
        y='total_ingresos',
        z='dias_proyeccion',
        color='cluster',
        hover_data=['titulo', 'genero'],
        title='Clusters de Películas (3D)',
        labels={
            'total_boletos': 'Boletos Vendidos',
            'total_ingresos': 'Ingresos ($)',
            'dias_proyeccion': 'Días en Proyección'
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Análisis por cluster
    st.subheader("Características de cada Cluster")
    
    cluster_stats = df_features.groupby('cluster').agg({
        'total_boletos': 'mean',
        'total_ingresos': 'mean',
        'precio_promedio': 'mean',
        'titulo': 'count'
    }).round(2)
    cluster_stats.columns = ['Boletos Promedio', 'Ingresos Promedio', 'Precio Promedio', 'Cantidad Películas']
    
    st.dataframe(cluster_stats, use_container_width=True)
    
    # Top películas por cluster
    for cluster_id in range(n_clusters):
        with st.expander(f"Cluster {cluster_id} - Top 5 Películas"):
            top_cluster = df_features[df_features['cluster'] == cluster_id].nlargest(5, 'total_ingresos')[['titulo', 'genero', 'total_ingresos']]
            st.dataframe(top_cluster, use_container_width=True)

# ============================================
# DASHBOARD 4: DETECCIÓN DE ANOMALÍAS
# ============================================
elif dashboard == "⚠️ Detección de Anomalías (IA)":
    st.header("Detección de Anomalías con Isolation Forest")
    st.info("📌 Utilizando Isolation Forest - Algoritmo de detección de outliers")
    
    # Datos de ventas diarias
    query_anomalias = """
    SELECT 
        t.fecha,
        SUM(fv.cantidad_boletos) as boletos,
        SUM(fv.ingreso_total) as ingresos,
        COUNT(DISTINCT fv.pelicula_id) as peliculas
    FROM fact_ventas fv
    JOIN dim_tiempo t ON fv.tiempo_id = t.tiempo_id
    GROUP BY t.fecha
    ORDER BY t.fecha
    """
    df_anomalias = query_to_df(query_anomalias)
    
    # Preparar features
    features = df_anomalias[['boletos', 'ingresos', 'peliculas']]
    
    # Isolation Forest
    contamination = st.slider("Sensibilidad (% esperado de anomalías)", 0.01, 0.10, 0.05)
    
    with st.spinner('Detectando anomalías...'):
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        df_anomalias['anomalia'] = iso_forest.fit_predict(features)
        df_anomalias['es_anomalia'] = df_anomalias['anomalia'] == -1
    
    # Visualización
    fig = px.scatter(
        df_anomalias,
        x='fecha',
        y='ingresos',
        color='es_anomalia',
        title='Detección de Anomalías en Ingresos Diarios',
        labels={'ingresos': 'Ingresos ($)', 'fecha': 'Fecha'},
        color_discrete_map={True: 'red', False: 'blue'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    total_dias = len(df_anomalias)
    anomalias_detectadas = df_anomalias['es_anomalia'].sum()
    porcentaje = (anomalias_detectadas / total_dias) * 100
    
    col1.metric("Total Días Analizados", total_dias)
    col2.metric("Anomalías Detectadas", anomalias_detectadas)
    col3.metric("Porcentaje", f"{porcentaje:.2f}%")
    
    # Lista de anomalías
    st.subheader("Días con Comportamiento Anómalo")
    anomalias_df = df_anomalias[df_anomalias['es_anomalia']][['fecha', 'boletos', 'ingresos', 'peliculas']].sort_values('fecha', ascending=False)
    st.dataframe(anomalias_df.head(20), use_container_width=True)
