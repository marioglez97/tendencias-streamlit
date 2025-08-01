import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
from io import BytesIO

# Configuración de la app
st.set_page_config(page_title="Buscador Avanzado de Tendencias", page_icon="📊", layout="centered")

st.title("📊 Buscador Avanzado de Tendencias con Google Trends")
st.write("Consulta tendencias, compara productos y descarga resultados.")

# Entradas del usuario
keywords = st.text_input("Escribe hasta 5 palabras separadas por coma (ej: air fryer, sneakers, robot aspiradora):", "air fryer, sneakers")
country = st.selectbox("Selecciona el país:", ["MX", "US", "ES", "AR", "CO"])
timeframe = st.selectbox("Periodo:", ["now 7-d", "today 3-m", "today 12-m", "today 5-y"])
geo_region = st.text_input("Código regional (opcional, ej. MX-NLE para Nuevo León):", "")

# Botón para ejecutar búsqueda
if st.button("Consultar Tendencia"):
    pytrends = TrendReq(hl='es-ES', tz=360)
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()][:5]  # Máx. 5 palabras
    geo = geo_region if geo_region else country

    with st.spinner("Consultando Google Trends..."):
        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo)
        data = pytrends.interest_over_time()

    if data.empty:
        st.error("No se encontraron datos para esas palabras.")
    else:
        st.success("Datos obtenidos correctamente.")

        # Mostrar tabla
        st.subheader("Datos de Interés en el Tiempo")
        st.dataframe(data[kw_list])

        # Crear gráfico
        fig, ax = plt.subplots(figsize=(10, 5))
        for col in kw_list:
            ax.plot(data.index, data[col], label=col)
        ax.set_title("Tendencias de Búsqueda")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Interés")
        ax.legend()
        st.pyplot(fig)

        # Botón para descargar gráfico como imagen
        buffer = BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)
        st.download_button(
            label="📥 Descargar Gráfico (PNG)",
            data=buffer,
            file_name="tendencias.png",
            mime="image/png"
        )

        # Botón para descargar CSV
        csv = data.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Descargar Datos (CSV)",
            data=csv,
            file_name="tendencias.csv",
            mime="text/csv"
        )

        # Términos relacionados
        st.subheader("Términos Relacionados")
        related_queries = {}
        for kw in kw_list:
            related = pytrends.related_queries().get(kw, {})
            if related and "top" in related and related["top"] is not None:
                related_queries[kw] = related["top"].head(10)

        if related_queries:
            for kw, df in related_queries.items():
                st.write(f"🔍 Palabra clave: {kw}")
                st.table(df)
        else:
            st.write("No se encontraron términos relacionados.")

