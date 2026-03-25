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
        font-size: 22px;
        text-transform: uppercase;
    }
    .sub-title {
        color: #555555;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        margin-top: 5px;
    }
    .info-text {
        color: #333333;
        font-weight: bold;
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 5px;
        border-left: 5px solid #004b87;
        margin-bottom: 25px;
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
    .share-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 10px;
        color: white !important;
    }
    .viber-btn { background-color: #7360f2; }
    .email-btn { background-color: #ea4335; }
    .google-btn { background-color: #34a853; }
    
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

# 4. КОНФИГУРАЦИЯ
try:
    API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except:
    st.error("Грешка при API ключа!")
    st.stop()

st.markdown("<p class='info-text'>📍 Начална точка: Производствена база - гр. Бургас</p>", unsafe_allow_html=True)

# 5. ВХОДНИ ДАННИ
c1, c2 = st.columns([1, 2])
with c1:
    km_price = st.number_input("Цена (€/км):", value=1.50, step=0.10)
with c2:
    customer_addr = st.text_input("Адрес на клиента:", placeholder="Град, улица...")

if st.button("ИЗЧИСЛИ ТРАНСПОРТ"):
    if customer_addr:
        try:
            lat, lng = 42.57318447773442, 27.495216046397218
            factory_coords = (lat, lng)
            directions = gmaps.directions(factory_coords, customer_addr, mode="driving", language="bg")
            
            if directions:
                res = directions[0]
                dist_km = res['legs'][0]['distance']['value'] / 1000
                total_cost = dist_km * km_price
                
                st.markdown("---")
                st.metric("Разстояние", f"{dist_km:.1f} км")
                st.metric("Цена (без ДДС)", f"{total_cost:.2f} €")
                
                # ПОДГОТОВКА НА СЪОБЩЕНИЕТО
                msg = f"ГЕОТОН - Транспортна калкулация:\nАдрес: {customer_addr}\nРазстояние: {dist_km:.1f} км\nЦена: {total_cost:.2f} € без ДДС"
                msg_encoded = urllib.parse.quote(msg)
                
                # БУТОНИ ЗА СПОДЕЛЯНЕ
                col_g, col_v, col_e = st.columns(3)
                
                with col_g:
                    google_link = f"https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={urllib.parse.quote(customer_addr)}"
                    st.markdown(f'<a href="{google_link}" target="_blank" class="share-btn google-btn">Google Maps</a>', unsafe_allow_html=True)
                
                with col_v:
                    viber_link = f"viber://forward?text={msg_encoded}"
                    st.markdown(f'<a href="{viber_link}" class="share-btn viber-btn">Viber</a>', unsafe_allow_html=True)
                
                with col_e:
                    email_link = f"mailto:?subject=Транспортна калкулация - ГЕОТОН&body={msg_encoded}"
                    st.markdown(f'<a href="{email_link}" class="share-btn email-btn">Имейл</a>', unsafe_allow_html=True)
                
                # КАРТА
                polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                route_line = [[p['lat'], p['lng']] for p in polyline_points]
                m = folium.Map()
                sw, ne = [min(p[0] for p in route_line), min(p[1] for p in route_line)], [max(p[0] for p in route_line), max(p[1] for p in route_line)]
                m.fit_bounds([sw, ne])
                folium.PolyLine(route_line, color="#004b87", weight=6).add_to(m)
                folium.Marker(route_line[0], icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
                folium.Marker(route_line[-1], icon=folium.Icon(color='green', icon='truck', prefix='fa')).add_to(m)
                st_folium(m, width="100%", height=400, returned_objects=[])
        except Exception as e:
            st.error(f"Грешка: {e}")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 11px;'>© 2026 ГЕОТОН БЕТОНОВИ ИЗДЕЛИЯ ООД</p>", unsafe_allow_html=True)
