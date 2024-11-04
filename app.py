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

# menú de navegación
def sidebar_menu():
    st.sidebar.header("")
    st.sidebar.image("logo.png", width=200)
    st.sidebar.markdown("---")
    
    selected_page = st.sidebar.radio(
        "Selecciona una página:",
        ["Inicio", "Estudiantes Extranjeros por Provincia", "Distribución de Nacionalidades Extranjeras en Argentina",
        "Beneficios Alimenticios Gratuitos","Infraestructuras Escolares Esenciales", "Sectores Público y Privado",
        "A tener en cuenta", "Contacto"],
        index=0
    )
    return selected_page

def home():
    st.title("Distribución de Migrantes Estudiantes y Condiciones Estructurales de las Escuelas Argentinas")

    st.write(
        """
        Esta aplicación presenta, desde los datos que recolectamos, las condiciones estructurales
        de los distintos establecimientos educativos a los que asisten niños/as y adolescentes migrantes
        en Argentina, como también nos permite visualizar la distribución de las distintas nacionalidades
        de los mismos en las provincias del país, con un recorte particular en los cuatro países con mayor
        cantidad de migrantes: Bolivia, Paraguay, Perú y Venezuela. Se pueden encontrar datos sobre la
        infraestructa de los establecimientos académicos, la presencia o no de servicios y/o beneficios
        públicos y gratuitos dentro de los mismos y otros factores relevantes para estos grupos.
        """
    )


def general():
    st.title("Distribución de Nacionalidades Extranjeras en Argentina")
    st.markdown("---")
    st.write(
        """
        En esta sección podes conocer cómo se distribuyen los/as alumnos/as extranjeros/as
        de nivel primario y secundario en Argentina mediante gráficos de barras.
        Nos enfocaremos en las nacionalidades más representativas en cantidad en el país:
        Bolivia, Paraguay, Perú y Venezuela. Se presentan especialmente las cinco provincias
        con mayor concentración de estas comunidades migrantes, lo que permitirá comprender
        mejor su distribución a nivel nacional.
        """
    )
    

    
    col1, col2= st.columns([2, 1])

    with col1:
        year = st.selectbox("Selecciona el año:", range(2011, 2024))
        st.markdown("---")
    
    countries = ["Bolivia", "Paraguay", "Perú", "Venezuela"]

    for i, country in enumerate(countries):
        with col1:
            st.subheader(country)
            if year >= 2014 or country != "Venezuela":
                image_file = f"distribucion/{year}/distribucion_{country}en_el_pais{year}.png"
                st.image(image_file, use_column_width='auto')
            else:
                st.write(f"Sin datos para el año {year}")
            st.markdown("---")
    
def estudiantes_extranjeros_por_provincia():
        
    st.title("Estudiantes Extranjeros por provincia")

    year = st.selectbox("Selecciona el año:", range(2011, 2024))

    with st.expander(f"Información Completa del año {year}", expanded=False):
        col1, col2, col3 = st.columns([0.7, 2, 0.7])
        with col2:
            st.image(f"extranjeros_por_provincia/tabla_distribucion_nacionalidades_{year}.png", width=800) 

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
                'porcentaje_Bolivia': float(row['porcentaje_Bolivia']),
                'porcentaje_Paraguay': float(row['porcentaje_Paraguay']),
                'porcentaje_Perú': float(row['porcentaje_Perú']),
                'porcentaje_Otros': float(row['porcentaje_Otros'])
            })

            # datos de Venezuela discriminados a partir de 2014 en adelante
            if 'porcentaje_Venezuela' in row.columns:
                feature['properties'].update({
                    'porcentaje_Venezuela': float(row['porcentaje_Venezuela']),
                })

    mapa = folium.Map(location=[-40.4161, -63.6167], zoom_start=4, scrollWheelZoom=False)

    fields = ['nombre', 'porcentaje_Bolivia', 'porcentaje_Paraguay', 'porcentaje_Perú']
    aliases = ["Provincia", "% Bolivia:", "% Paraguay:", "% Perú:"]

    if year >= 2014:
        fields.append('porcentaje_Venezuela')
        fields.append('porcentaje_Otros')
        aliases.append("% Venezuela:")
        aliases.append("% Otros:")
    else:
        fields.append('porcentaje_Otros')
        aliases.append("% Otros:")


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
            fields=fields,
            aliases=aliases,
            localize=True,
            sticky=True
        )
    ).add_to(mapa)

    col1, col2 = st.columns([1.7, 3.3])

    with col1:

        st_mapa = st_folium(mapa, width=400, height=600)

        prov = ''
        if st_mapa['last_active_drawing']:
            prov = st_mapa['last_active_drawing']['properties']['nombre']


    with col2:
        st.write(
            """
            Este mapa ilustra la distribución de las diversas nacionalidades extranjeras
            de los/as estudiantes migrantes que asisten a escuelas primarias y secundarias
            en cada provincia de la Argentina para el año seleccionado. Al pasar el mouse
            sobre una provincia, se despliega información detallada con los porcentajes
            correspondientes a cada nacionalidad presente en esa región. Al hacer click
            en una provincia, se mostrarán los valores totales en relación con esos
            porcentajes, brindando una visión más clara de cómo se distribuyen las
            nacionalidades en el sistema educativo argentino.
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
    
def beneficios():
    st.title("Beneficios Alimenticios Gratuitos")
    st.write(
        """
        Esta sección presenta la información detallada sobre los establecimientos
        educativos divididos en primario y secundario, que ofrecen a sus alumnos/as
        beneficios alimenticios gratuitos a lo largo del país. Podrás explorar estos
        datos separándolos por año y por nivel educativo. Los porcentajes reflejan la
        cantidad de establecimientos que ofrecen el beneficio, destacamos la importancia
        del acceso a la alimentación para un fructífero desarrollo de los/as estudiantes.
        """
    )

    year = st.selectbox("Selecciona el año:", range(2011, 2024))
    nivel = st.selectbox("Selecciona el nivel educativo:", ["Primaria", "Secundaria"])
    nivel = nivel.lower()

    opciones_tipo = {
        "Escuelas con extranjeros": "con_extranjeros",
        "Escuelas sin extranjeros": "sin_extranjeros",
        "Total de escuelas": ""
    }

    seleccion = st.selectbox("Selecciona el tipo de escuela:", list(opciones_tipo.keys()))

    tipo = opciones_tipo[seleccion]

    st.markdown("---")

    c1, c2= st.columns([1,0.7])
    with c2:
        if (tipo == ''):
            st.image(f"beneficios_alimenticios/{nivel}/escuelas_{nivel}s_con_y_sin_comida_{year}.png", width=530)
        else:
            st.image(f"beneficios_alimenticios/{nivel}/{tipo}/escuelas_{nivel}s_{tipo}_con_y_sin_comida_{year}.png", width=530)

    with c1:
        if (tipo == ''):
            st.image(f"beneficios_alimenticios/{nivel}/barras_por_provincia_escuelas_{nivel}s_con_y_sin_comida_{year}.png", width=830)
        else:
            st.image(f"beneficios_alimenticios/{nivel}/{tipo}/barras_por_provincia_escuelas_{nivel}s_{tipo}_con_y_sin_comida_{year}.png", width=830)


def sector():
    st.title("Sectores Público y Privado")
    st.write(
        """
        En esta sección comparamos la distribución de los establecimientos educativos
        que ofrecen un servicio público o privado a sus alumnos/as en Argentina.
        Puedes seleccionar diferentes años y opciones de los establecimientos para
        observar cómo se distribuyen las instituciones educativas y cómo varía según
        la presencia de estudiantes extranjeros/as según cada servicio. Este análisis
        es clave para entender las dinámicas de inclusión para la población migrante
        y el acceso gratuito o pago que tienen en la educación en el país.
        """
    )

    year = st.selectbox("Selecciona el año:", range(2011, 2024))

    opciones_tipo = {
        "Total de escuelas": "",
        "Escuelas con extranjeros": "extranjeros_",
        "Escuelas sin extranjeros": "sin_extranjeros_"
    }

    seleccion = st.selectbox("Selecciona el tipo de escuela:", list(opciones_tipo.keys()))

    tipo = opciones_tipo[seleccion]

    st.markdown("---")

    c1, c2= st.columns([1,1])
    with c2:
        col1, col2 = st.columns([0.2,2])
        with col2:
            st.image(f"sector/{year}/grafico_torta_escuelas_sector_{tipo}{year}.png", width=570)

    with c1:
            st.image(f"sector/{year}/porcentaje_de_escuelas_por_provincia_sector_{tipo}{year}.png", width=690)


    
def infraestructura():
    st.title("Infraestructuras Escolares Esenciales")
    st.write(
        """
        En esta sección exploramos las condiciones de infraestructura de los establecimientos
        educativos a los que asisten estudiantes migrantes de los niveles primario y secundario
        en toda la Argentina. Analizamos aspectos clave como la disponibilidad de bibliotecas,
        la conexión a internet y si cuentan con electricidad, consideradas como elementos y
        necesidades esenciales para un ambiente de aprendizaje. Esta información permite comprender
        y visibilizar claramente las oportunidades y desafíos que enfrentan estas instituciones en
        cuanto a recursos y servicios básicos.
        """
    )

    opciones_tipo_torta = {
        "biblioteca": {
            "Escuelas con extranjeros": "extranjeros_",
            "Escuelas sin extranjeros": "sin_extranjeros_",
            "Total de escuelas": ""
        },
        "electricidad": {
            "Escuelas con extranjeros": "extranjeros_",
            "Escuelas sin extranjeros": "sin_extranjeros_",
            "Total de escuelas": ""
        },
        "internet": {
            "Escuelas con extranjeros": "extranjeros_",
            "Escuelas sin extranjeros": "sin_extranjeros_",
            "Total de escuelas": "nacional_"
        }
    }

    opciones_tipo_barra = {
        "biblioteca": {
            "Escuelas con extranjeros": "extranjeros_",
            "Escuelas sin extranjeros": "sin_extranjeros_",
            "Total de escuelas": ""
        },
        "electricidad": {
            "Escuelas con extranjeros": "extranjeros_",
            "Escuelas sin extranjeros": "sin_extranjeros_",
            "Total de escuelas": ""
        },
        "internet": {
            "Escuelas con extranjeros": "extranjeros_",
            "Escuelas sin extranjeros": "sin_extranjeros_",
            "Total de escuelas": "total_"
        }
    }

    opciones_torta = {
        "biblioteca": "disponibilidad_biblioteca",
        "electricidad": "acceso_electricidad_nacional",
        "internet": "acceso_internet"
    }

    opciones_barra = {
        "biblioteca": "disponibilidad_biblioteca",
        "electricidad": "tipo_electricidad",
        "internet": "tipo_internet"
    }

    infraestructura = st.selectbox("Selecciona el recurso de infraestructura:", ["Electricidad", "Conexión a Internet", "Biblioteca"])
    infraestructura = "internet" if infraestructura == "Conexión a Internet" else infraestructura
    infraestructura = infraestructura.lower()

    seleccion = st.selectbox("Selecciona el tipo de escuela:", ["Total de escuelas", "Escuelas con extranjeros", "Escuelas sin extranjeros"])

    year = st.selectbox("Selecciona el año:", range(2011, 2024))

    st.markdown("---")

    c1, c2= st.columns([1,1])
    with c2:
        if (infraestructura != "biblioteca" or year != 2011):
            col1, col2 = st.columns([0.2,2])
            with col2:
                    st.image(f"infraestructura/{infraestructura}/{year}/grafico_torta_{opciones_torta[infraestructura]}_{opciones_tipo_torta[infraestructura][seleccion]}{year}.png", width=570)
        else:
            st.write(f"Sin Datos para el año {year}")
    with c1:
        if (infraestructura != "biblioteca" or year != 2011):
            st.image(f"infraestructura/{infraestructura}/{year}/porcentaje_de_escuelas_por_provincia_{opciones_barra[infraestructura]}_{opciones_tipo_barra[infraestructura][seleccion]}{year}.png", width=690)
        else:
            st.write(f"Sin Datos para el año {year}")

def analisis():
    st.title("A tener en cuenta")
    text = """
    Al explorar los datos presentados en esta aplicación, es importante considerar ciertos factores que pueden influir en los resultados y su interpretación

    1. **Posibles mediciones extremas:** Algunos valores pueden parecer anormalmente altos o bajos. Esto ocurre en ciertas ocasiones debido a la falta de datos representativos, ya que las mediciones realizadas sobre una base de datos pequeña o incompleta pueden mostrar tendencias o extremos que no reflejan el panorama general.

    2. **Desestimación de datos inconsistentes:** Para asegurar la calidad de los análisis, ciertos registros fueron excluidos debido a inconsistencias en la información. Un ejemplo de esto son aquellos casos en los que las escuelas reportaron alumnos extranjeros en cierto nivel educativo, pero al mismo tiempo, no declararon matrícula de estudiantes en dicho nivel. Estas discrepancias podrían generar confusión y afectar la precisión de las visualizaciones, por lo cual estos datos fueron descartados en nuestro trabajo.

    3. **Consideración sobre la disponibilidad de datos:** Cuando se indica "sin datos" para un año específico, no significa necesariamente que no existan campos con información en la base de datos correspondiente. En algunos casos, aunque esta columna está presente, los datos no fueron relevados en los cuadernillos de relevamiento anual. Por ejemplo, entre 2011 y 2013, Venezuela se contaba como 'Otros países de América', y aunque desde 2012 se tiene una columna propia en la base de datos, la información sobre esta nacionalidad aparece discriminada en los cuadernillos de relevamiento a partir de 2014.
    Asimismo, la columna correspondiente a la disponibilidad de biblioteca está presente en la base de datos de 2011, pero tampoco fue relevada en los cuadernillos de ese año, comenzando a ser registrada a partir del año siguiente. Estas distinciones son clave al analizar la información, ya que reflejan cómo se han categorizado los datos a lo largo del tiempo.

    Al tener en cuenta estas observaciones, se busca que los resultados sean lo más claros y precisos posibles. Sin embargo, invitamos a los usuarios a interpretar los datos con un grado de prudencia, especialmente cuando se observan valores que se alejan de las tendencias generales.
    """

    st.markdown(text)

def contacto():
    st.title("Contacto")
    st.write("Si tienes preguntas o feedback, no dudes en contactarnos.")
    st.subheader("Formulario de Contacto")

    FORMSUBMIT_URL = "https://formsubmit.co/angeles.carrara@mi.unc.edu.ar"

    name = st.text_input("Tu Nombre")
    email = st.text_input("Tu Correo Electrónico")
    message = st.text_area("Tu Mensaje")

    if st.button("Enviar"):
        if name and email and message:
            form_data = {
                'name': name,
                'email': email,
                'message': message
            }
            response = requests.post(FORMSUBMIT_URL, data=form_data)
            
            if response.status_code == 200:
                st.success("¡Mensaje enviado con éxito!")
            else:
                st.error("Error al enviar el mensaje.")
        else:
            st.warning("Por favor, completa todos los campos.")



def main():
    st.set_page_config(page_title="Calidad de Escuelas en Argentina", layout="wide")

    # Menú de selección de página
    selected_page = sidebar_menu()

    # Mostrar la página seleccionada
    if selected_page == "Inicio":
        home()
    elif selected_page == "Distribución de Nacionalidades Extranjeras en Argentina":
        general()
    elif selected_page == "Estudiantes Extranjeros por Provincia":
        prov = estudiantes_extranjeros_por_provincia()
    elif selected_page == "Beneficios Alimenticios Gratuitos":
        beneficios()
    elif selected_page == "Sectores Público y Privado":
        sector()
    elif selected_page == "Infraestructuras Escolares Esenciales":
        infraestructura()
    elif selected_page == "A tener en cuenta":
        analisis()
    elif selected_page == "Contacto":
        contacto()

if __name__ == "__main__":
    main()

