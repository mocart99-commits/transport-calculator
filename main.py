import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium

# 1. Настройка на страницата
st.set_page_config(
    page_title="GEOTON | Транспортен Калкулатор", 
    layout="centered", 
    page_icon="🏗️"
)

# Стилизиране с CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: -40px;
    }
    .main-title {
        color: #004b87;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0px;
        margin-top: -20px;
    }
    .sub-title {
        color: #555555;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        text-align: center;
        margin-bottom: 30px;
    }
    .info-text {
        color: #333333;
        font-weight: bold;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #004b87;
        margin-bottom: 20px;
    }
    div.stButton > button:first-child {
        background-color: #004b87;
        color: white;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        font-size: 18px;
        border: none;
        margin-top: 20px;
    }
    /* Премахваме излишните разстояния при логото */
    [data-testid="stImage"] {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ЛОГО И ЗАГЛАВИЯ
# Използваме logo.jpg с фиксирана ширина
try:
    st.image("logo.jpg", width=250)
except:
    st.markdown("<h1 style='text-align:center;'>GEOTON</h1>", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>Транспортен Калкулатор</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Геотон бетонови изделия</p>", unsafe_allow_html=True)

# 3. КОНФИГУРАЦИЯ (Secrets)
try:
    API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
except Exception:
    st.error("Грешка: Липсва Google Maps API Key в Secrets!")
    st.stop()

gmaps = googlemaps.Client(key=API_KEY)

# 4. ВХОДНИ ДАННИ
st.markdown("<p class='info-text'>📍 Начална точка: Производствена база Геотон</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
with col1:
    km_price = st.number_input("Цена (€/км):", value=1.50, step=0.10)
with col2:
    customer_addr = st.text_input("Адрес на клиента:", placeholder="Град, улица, номер...")

# 5. ИЗЧИСЛЕНИЯ
if st.button("ИЗЧИСЛИ ТРАНСПОРТ"):
    if customer_addr:
        try:
            # Твоите координати
            factory_coords = (42.5749926, 27.4951604)
            
            directions = gmaps.directions(factory_coords, customer_addr, mode="driving", language="bg")
            
            if not directions:
                st.error("Адресът не е намерен! Моля, опитайте по-точно.")
            else:
                res = directions[0]
                dist_km = res['legs'][0]['distance']['value'] / 1000
                total_cost = dist_km * km_price
                
                # Показване на резултати в колони
                st.markdown("---")
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric("Разстояние", f"{dist_km:.1f} км")
                with res_col2:
                    st.metric("Цена (без ДДС)", f"{total_cost:.2f} €")
                
                # КАРТА
                polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                route_line = [[p['lat'], p['lng']] for p in polyline_points]
                
                m = folium.Map(location=route_line[0], zoom_start=8)
                folium.PolyLine(route_line, color="#004b87", weight=6, opacity=0.8).add_to(m)
                
                # Маркери
                folium.Marker(route_line[0], popup="Геотон", icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
                folium.Marker(route_line[-1], popup="Клиент", icon=folium.Icon(color='green', icon='truck', prefix='fa')).add_to(m)
                
                st_folium(m, width="100%", height=400, returned_objects=[])
                
        except Exception as e:
            st.error(f"Грешка: {e}")
    else:
        st.warning("Моля, въведете адрес.")

st.markdown("<br><hr><p style='text-align: center; color: gray; font-size: 12px;'>© 2024 ГЕОТОН - Всички права запазени</p>", unsafe_allow_html=True)
