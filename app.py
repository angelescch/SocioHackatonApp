import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
import requests
import json
from streamlit_folium import folium_static
from streamlit_folium import st_folium
from folium.features import GeoJsonTooltip

# Cargar datos
def load_data():
    # Aquí carga tus datos de calidad de escuelas y beneficios alimenticios
    return None, None, None

# Mapa de Argentina
def create_map():
    argentina_map = gpd.read_file("provincia/provincia.shp")
    m = folium.Map(location=[-38.4161, -63.6167], zoom_start=4)
    folium.GeoJson(argentina_map).add_to(m)
    return m

# Función para crear el menú de navegación
def sidebar_menu():
    st.sidebar.header("")
    st.sidebar.image("logo.jpg", width=250)  # Agrega un logo atractivo
    st.sidebar.markdown("---")
    
    selected_page = st.sidebar.radio(
        "Selecciona una página:",
        ["Inicio", "Distribución de Nacionalidades Extranjeras en Argentina", "Estudiantes Extranjeros por Provincia", 
         "Beneficios Alimenticios", "Sectores Público y Privado", 
         "Preferencias por Provincia", "Análisis por Año", "Contacto"],
        index=0  # Valor por defecto
    )
    return selected_page

# Páginas de contenido
def home():
    st.title("Bienvenido a la App de Calidad de Escuelas en Argentina")
    st.write(
    "Esta aplicación explora la calidad de las escuelas a las que asisten niños/as y adolescentes extranjeros en Argentina, "
    "con un enfoque particular en los cuatro países con mayor cantidad de migrantes: **Bolivia,** **Paraguay,** **Perú** y **Venezuela**. "
    "Aquí podrás encontrar datos sobre infraestructura, beneficios alimenticios, y otros factores relevantes para estos grupos."
    )


def general_data():
    st.title("Distribución de Nacionalidades Extranjeras en Argentina")
    st.markdown("---")
    st.write(
        """
        Conocé cómo se distribuyen los alumnos extranjeros en Argentina mediante
        gráficos de barras. Nos enfocaremos en las nacionalidades más
        representativas: Bolivia, Paraguay, Perú y Venezuela, y su presencia en
        las diversas provincias del país. Analizaremos especialmente las cinco
        provincias con mayor concentración de estas comunidades, lo que permitirá
        entender mejor su distribución a nivel nacional.
        """
    )
    
    year = st.selectbox("Selecciona el año:", range(2011, 2024)) 
    
    # Gráficos por país
    countries = ["Bolivia", "Paraguay", "Perú", "Venezuela"]
    
    # Dividir en columnas
    cols = st.columns(2)  # Crea dos columnas

    for i, country in enumerate(countries):
        with cols[i % 2]:  # Alternar columnas
            st.subheader(country)
            if year >= 2014 or country != "Venezuela":
                image_file = f"distribucion/{year}/distribucion_{country}_en_el_pais_{year}.png"  # Cambiar según la convención de nombres
                st.image(image_file, caption=f"Distribución de {country} en el año {year}", use_column_width='auto')
            else:
                st.write(f"Sin datos para el año {year}")
    
def estudiantes_extranjeros_por_provincia():
    st.markdown(
        """
        <script>
        window.onscroll = function() {
            if (document.body.scrollTop === 0 || document.documentElement.scrollTop === 0) {
                location.reload();
            }
        };
        </script>
        """,
        unsafe_allow_html=True
    )
        
    st.title("Estudiantes Extranjeros por provincia")

    year = st.selectbox("Selecciona el año:", range(2011, 2024))
    st.markdown("---")


    csv_path = f"extranjeros_por_provincia/porcentaje_extranjeros_por_provincia_{year}.csv"
    data = pd.read_csv(csv_path)

    geojson_path = 'provincias.geojson'
    with open(geojson_path, 'r') as f:
        provincias_geojson = json.load(f)

    for feature in provincias_geojson['features']:
        provincia = feature['properties']['nombre']  
        row = data[data['provincia'] == provincia]
        
        if not row.empty:
            feature['properties'].update({
                'total_extranjeros': int(row['total_extranjeros']),
                'Bolivia': int(row['Bolivia']),
                'Paraguay': int(row['Paraguay']),
                'Perú': int(row['Perú']),
                'Otros': int(row['Otros']),
                'porcentaje_Bolivia': float(row['porcentaje_Bolivia']),
                'porcentaje_Paraguay': float(row['porcentaje_Paraguay']),
                'porcentaje_Perú': float(row['porcentaje_Perú']),
                'porcentaje_Otros': float(row['porcentaje_Otros'])
            })

    mapa = folium.Map(location=[-40.4161, -63.6167], zoom_start=4, scrollWheelZoom=False)


    folium.GeoJson(
        provincias_geojson,
        name="Provincias",
        style_function=lambda x: {
            'fillColor': '#ff1493',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.4,
        },
        tooltip=GeoJsonTooltip(
            fields=[
                'nombre',
                'porcentaje_Bolivia', 'porcentaje_Paraguay', 'porcentaje_Perú', 'porcentaje_Otros'
            ],
            aliases=[
                "Provincia",
                "% Bolivia:", "% Paraguay:", "% Perú:", "% Otros:"
            ],
            localize=True,
            sticky=True
        )
    ).add_to(mapa)

    col1, col2 = st.columns([1.7, 3.3])

    # Mostrar el mapa en la columna izquierda
    with col1:

        st_mapa = st_folium(mapa, width=400, height=600)

        prov = ''
        if st_mapa['last_active_drawing']:
            prov = st_mapa['last_active_drawing']['properties']['nombre']


    with col2:
        st.subheader("Información Adicional")
        st.write(
            """
            Este mapa muestra la distribución de nacionalidades extranjeras en
            cada provincia de Argentina para el año seleccionado. Al pasar el
            mouse sobre una provincia, se despliega información detallada con
            los porcentajes correspondientes a cada nacionalidad en ese territorio.
            Al hacer clic en una provincia, se especificarán los valores totales
            en relación con esos porcentajes.
            """
        )
        if (prov != ''):
            row = data[data['provincia'] == prov]
            if not row.empty:
                st.subheader(f'Datos para {prov} en el año {year}')
                string_format = "{:,}"
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                with c1:
                    st.metric("Total Extranjeros", string_format.format(int(row['total_extranjeros'])))
                with c2:
                    st.metric("Bolivia", string_format.format(int(row['Bolivia'])))
                with c3:
                    st.metric("Paraguay", string_format.format(int(row['Paraguay'])))
                with c4: 
                    st.metric("Perú", string_format.format(int(row['Perú'])))
                with c5:
                    if (year <= 2013):
                        st.metric("Otros", string_format.format(int(row['Otros'])))
                    else:
                        st.metric("Venezuela", string_format.format(int(row['Venezuela'])))
                with c6:
                    if (year >= 2014):
                        st.metric("Otros", string_format.format(int(row['Otros'])))

  
    return prov
    
def benefits_data():
    st.title("Beneficios Alimenticios")
    st.write("Información sobre los beneficios alimenticios disponibles en las escuelas...")

def sector_data():
    st.title("Sectores Público y Privado")
    st.write("Comparación de la cantidad de escuelas en el sector público versus el privado...")
    
def preferences_data():
    st.title("Preferencias por Provincia")
    m = create_map()
    folium_static(m)

def year_analysis():
    st.title("Análisis por Año")
    year = st.selectbox("Selecciona el año:", range(2011, 2024))
    st.write(f"Datos del año {year}...")

def contact_page():
    st.title("Contacto")
    st.write("Si tienes preguntas o feedback, no dudes en contactarnos.")


def main():
    st.set_page_config(page_title="Calidad de Escuelas en Argentina", layout="wide")
    
    df_quality, df_benefits, df_population = load_data()
    
    # Menú de selección de página
    selected_page = sidebar_menu()

    # Mostrar la página seleccionada
    if selected_page == "Inicio":
        home()
    elif selected_page == "Distribución de Nacionalidades Extranjeras en Argentina":
        general_data()
    elif selected_page == "Estudiantes Extranjeros por Provincia":
        prov = estudiantes_extranjeros_por_provincia()
    elif selected_page == "Beneficios Alimenticios":
        benefits_data()
    elif selected_page == "Sectores Público y Privado":
        sector_data()
    elif selected_page == "Preferencias por Provincia":
        preferences_data()
    elif selected_page == "Análisis por Año":
        year_analysis()
    elif selected_page == "Contacto":
        contact_page()

if __name__ == "__main__":
    main()

# esto anda muestra el mapa de argentina con las provincias
# def quality_data():

#     with open("provincias.geojson", "r", encoding="utf-8") as f:
#         geojson_data = json.load(f)

#     # Configura el centro del mapa y el nivel de zoom inicial
#     m = folium.Map(location=[-38.4161, -63.6167], zoom_start=4)

#     # Añade el GeoJSON al mapa
#     folium.GeoJson(
#         geojson_data,
#         name="Provincias de Argentina",
#         tooltip=folium.GeoJsonTooltip(fields=["nombre"], aliases=["Provincia:"])
#     ).add_to(m)

#     # Muestra el mapa en la app de Streamlit
#     st.title("Mapa de Argentina con Provincias")
#     st_folium(m, width=700, height=500)
