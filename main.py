import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="GEOTON | Транспортен Калкулатор", 
    layout="centered", 
    page_icon="🏗️"
)

# CSS за изчистен дизайн и премахване на бутона за цял екран
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* Премахване на бутона за уголемяване на картинката */
    button[title="Enlarge image"] {
        display: none !important;
    }
    
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-bottom: -50px;
        margin-top: -20px;
    }
    .main-title {
        color: #004b87;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #555555;
        font-family: 'Arial', sans-serif;
        font-size: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    .info-text {
        color: #333333;
        font-weight: bold;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #004b87;
    }
    div.stButton > button:first-child {
        background-color: #004b87;
        color: white;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Лого
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        # Добавяме параметри за изключване на интерактивността
        st.image("logo.jpg", width=280)
    except:
        st.markdown("<h1 style='text-align:center;'>GEOTON</h1>", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Транспортен Калкулатор</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Геотон бетонови изделия</p>", unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except:
    st.error("Липсва API Key!")
    st.stop()

st.markdown("<p class='info-text'>📍 Начална точка: Производствена база Геотон</p>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 2])
with c1:
    km_price = st.number_input("Цена (€/км):", value=1.50, step=0.10)
with c2:
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
                res_c1, res_c2 = st.columns(2)
                res_c1.metric("Разстояние", f"{dist_km:.1f} км")
                res_c2.metric("Цена (без ДДС)", f"{total_cost:.2f} €")
                
                polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                route_line = [[p['lat'], p['lng']] for p in polyline_points]
                m = folium.Map(location=route_line[0], zoom_start=8)
                folium.PolyLine(route_line, color="#004b87", weight=6).add_to(m)
                folium.Marker(route_line[0], icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
                folium.Marker(route_line[-1], icon=folium.Icon(color='green', icon='truck', prefix='fa')).add_to(m)
                st_folium(m, width="100%", height=400, returned_objects=[])
        except Exception as e:
            st.error(f"Грешка: {e}")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 11px;'>© 2024 ГЕОТОН - Бургас</p>", unsafe_allow_html=True)
