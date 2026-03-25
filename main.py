import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium
import urllib.parse

# 1. Настройка на страницата
st.set_page_config(
    page_title="ГЕОТОН | Транспортен Калкулатор", 
    layout="centered", 
    page_icon="🏗️"
)

# 2. CSS Стилизиране
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    .geoton-header {
        text-align: center;
        margin-top: -50px;
        margin-bottom: 30px;
        padding: 10px;
    }
    .main-title {
        color: #004b87;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 24px; /* Малко по-малък размер, за да се събере на един ред */
        text-transform: uppercase;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #555555;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        margin-top: 5px;
        font-weight: normal;
    }
    .info-text {
        color: #333333;
        font-weight: bold;
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 5px;
        border-left: 5px solid #004b87;
        margin-bottom: 25px;
        font-size: 14px;
    }
    div.stButton > button:first-child {
        background-color: #004b87;
        color: white;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        border: none;
        margin-top: 10px;
        font-size: 16px;
    }
    .google-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #34a853;
        color: white !important;
        padding: 12px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
        font-size: 15px;
    }
    /* Скриване на излишни елементи */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. ЗАГЛАВИЯ
st.markdown("""
    <div class="geoton-header">
        <div class="main-title">ГЕОТОН БЕТОНОВИ ИЗДЕЛИЯ ООД</div>
        <div class="sub-title">Транспортен Калкулатор</div>
    </div>
    """, unsafe_allow_html=True)

# 4. КОНФИГУРАЦИЯ (Secrets)
try:
    API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.error("Грешка при зареждане на API ключа!")
    st.stop()

st.markdown("<p class='info-text'>📍 Начална точка: Производствена база - гр. Бургас</p>", unsafe_allow_html=True)

# 5. ВХОДНИ ДАННИ
c1, c2 = st.columns([1, 2])
with c1:
    km_price = st.number_input("Цена (€/км):", value=1.50, step=0.10, format="%.2f")
with c2:
    customer_addr = st.text_input("Адрес на клиента:", placeholder="Град, улица, номер...")

# 6. ЛОГИКА И ИЗЧИСЛЕНИЯ
if st.button("ИЗЧИСЛИ ТРАНСПОРТ"):
    if customer_addr:
        try:
            # ТВОИТЕ ТОЧНИ GPS КООРДИНАТИ
            lat, lng = 42.57318447773442, 27.495216046397218
            factory_coords = (lat, lng)
            
            directions = gmaps.directions(factory_coords, customer_addr, mode="driving", language="bg")
            
            if directions:
                res = directions[0]
                dist_km = res['legs'][0]['distance']['value'] / 1000
                total_cost = dist_km * km_price
                
                st.markdown("---")
                res_c1, res_c2 = st.columns(2)
                res_c1.metric("Разстояние", f"{dist_km:.1f} км")
                res_c2.metric("Цена (без ДДС)", f"{total_cost:.2f} €")
                
                # Линк за Google Maps Навигация
                destination_encoded = urllib.parse.quote(customer_addr)
                google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={destination_encoded}&travelmode=driving"
                
                st.markdown(f'<a href="{google_maps_link}" target="_blank" class="google-btn">Отвори в Google Maps за навигация ↗️</a>', unsafe_allow_html=True)
                
                # Карта за визуализация
                polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                route_line = [[p['lat'], p['lng']] for p in polyline_points]
                
                m = folium.Map(location=route_line[len(route_line)//2])
                
                # Автоматичен мащаб според маршрута
                sw = min(route_line, key=lambda x: x[0]), min(route_line, key=lambda x: x[1])
                ne = max(route_line, key=lambda x: x[0]), max(route_line, key=lambda x: x[1])
                m.fit_bounds([sw, ne]) 
                
                folium.PolyLine(route_line, color="#004b87", weight=6, opacity=0.8).add_to(m)
                folium.Marker(route_line[0], popup="ГЕОТОН", icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
                folium.Marker(route_line[-1], popup="Клиент", icon=folium.Icon(color='green', icon='truck', prefix='fa')).add_to(m)
                
                st_folium(m, width="100%", height=400, returned_objects=[])
            else:
                st.error("Адресът не е намерен. Моля, опитайте с по-конкретни данни.")
        except Exception as e:
            st.error(f"Грешка: {e}")
    else:
        st.warning("Моля, въведете адрес на клиента.")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 11px;'>© 2026 ГЕОТОН БЕТОНОВИ ИЗДЕЛИЯ ООД - Бургас</p>", unsafe_allow_html=True)
