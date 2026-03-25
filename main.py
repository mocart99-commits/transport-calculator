import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium

# 1. Настройка на страницата - Чисто бяла тема
st.set_page_config(
    page_title="GEOTON | Транспортен Калкулатор", 
    layout="centered", 
    page_icon="🏗️"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .main-title {
        color: #004b87;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-top: -30px;
    }
    .sub-title {
        color: #555555;
        font-family: 'Arial', sans-serif;
        font-size: 18px;
        text-align: center;
        margin-bottom: 20px;
    }
    div.stButton > button:first-child {
        background-color: #004b87;
        color: white;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ЛОГО - Използваме твоя файл logo.jpg
try:
    st.image("logo.jpg", use_container_width=True)
except:
    st.markdown("<h1 class='main-title'>GEOTON</h1>", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Транспортен Калкулатор</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Геотон бетонови изделия</p>", unsafe_allow_html=True)

# 3. КОНФИГУРАЦИЯ
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

st.markdown("---")
st.info("📍 Начална точка: Производствена база Геотон")

col1, col2 = st.columns([1, 2])
with col1:
    km_price = st.number_input("Цена (€/км):", value=1.50, step=0.10)
with col2:
    customer_addr = st.text_input("Адрес на клиента:", placeholder="Град, улица...")

if st.button("ИЗЧИСЛИ ТРАНСПОРТ"):
    if customer_addr:
        try:
            factory_coords = (42.5749926, 27.4951604)
            directions = gmaps.directions(factory_coords, customer_addr, mode="driving", language="bg")
            
            if directions:
                res = directions[0]
                dist_km = res['legs'][0]['distance']['value'] / 1000
                total_cost = dist_km * km_price
                
                st.markdown("---")
                c1, c2 = st.columns(2)
                c1.metric("Разстояние", f"{dist_km:.1f} км")
                c2.metric("Цена (без ДДС)", f"{total_cost:.2f} €")
                
                polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                route_line = [[p['lat'], p['lng']] for p in polyline_points]
                m = folium.Map(location=route_line[0], zoom_start=8)
                folium.PolyLine(route_line, color="#004b87", weight=6).add_to(m)
                folium.Marker(route_line[0], icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
                folium.Marker(route_line[-1], icon=folium.Icon(color='green', icon='truck', prefix='fa')).add_to(m)
                st_folium(m, width="100%", height=400, returned_objects=[])
        except Exception as e:
            st.error(f"Грешка: {e}")
