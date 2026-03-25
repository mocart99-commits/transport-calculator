import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium
import base64

# 1. Настройка на страницата
st.set_page_config(
    page_title="GEOTON | Транспортен Калкулатор", 
    layout="centered", 
    page_icon="🏗️"
)

# 2. Функция за логото (за премахване на бутона Enlarge)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def display_logo(file_path):
    try:
        bin_str = get_base64_of_bin_file(file_path)
        html_code = f'''
            <div style="display: flex; justify-content: center; margin-top: -20px; margin-bottom: 0px;">
                <img src="data:image/jpeg;base64,{bin_str}" style="width: 280px; pointer-events: none;">
            </div>
        '''
        st.markdown(html_code, unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='text-align:center; color:#004b87;'>GEOTON</h1>", unsafe_allow_html=True)

# 3. CSS Стилизиране за професионален вид
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* Скриване на системни иконки на Streamlit върху картинки */
    button[title="Enlarge image"], [data-testid="stImageHoverIcons"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    .main-title {
        color: #004b87;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-top: 5px;
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

# Показване на логото
display_logo("logo.jpg")

st.markdown("<h1 class='main-title'>Транспортен Калкулатор</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Геотон бетонови изделия</p>", unsafe_allow_html=True)

# 4. КОНФИГУРАЦИЯ (Secrets)
try:
    API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except:
    st.error("Липсва Google Maps API Key!")
    st.stop()

st.markdown("<p class='info-text'>📍 Начална точка: Производствена база Геотон</p>", unsafe_allow_html=True)

c1, c2 = st.columns([1, 2])
with c1:
    km_price = st.number_input("Цена (€/км):", value=1.50, step=0.10)
with c2:
    customer_addr = st.text_input("Адрес на клиента:", placeholder="Град, улица, номер...")

# 5. ИЗЧИСЛЕНИЯ
if st.button("ИЗЧИСЛИ ТРАНСПОРТ"):
    if customer_addr:
        try:
            # ТВОИТЕ GPS КООРДИНАТИ
            factory_coords = (42.57318447773442, 27.495216046397218)
            
            directions = gmaps.directions(factory_coords, customer_addr, mode="driving", language="bg")
            
            if directions:
                res = directions[0]
                dist_km = res['legs'][0]['distance']['value'] / 1000
                total_cost = dist_km * km_price
                
                st.markdown("---")
                res_c1, res_c2 = st.columns(2)
                res_c1.metric("Разстояние", f"{dist_km:.1f} км")
                res_c2.metric("Цена (без ДДС)", f"{total_cost:.2f} €")
                
                # Построяване на картата
                polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                route_line = [[p['lat'], p['lng']] for p in polyline_points]
                
                m = folium.Map(location=route_line[0], zoom_start=14)
                folium.PolyLine(route_line, color="#004b87", weight=6).add_to(m)
                
                folium.Marker(route_line[0], popup="Геотон", icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
                folium.Marker(route_line[-1], popup="Клиент", icon=folium.Icon(color='green', icon='truck', prefix='fa')).add_to(m)
                
                st_folium(m, width="100%", height=400, returned_objects=[])
            else:
                st.error("Неуспешно намиране на маршрут. Моля, проверете адреса.")
        except Exception as e:
            st.error(f"Грешка: {e}")
    else:
        st.warning("Моля, въведете адрес.")

st.markdown("<br><p style='text-align: center; color: gray; font-size: 11px;'>© 2024 ГЕОТОН - Бургас</p>", unsafe_allow_html=True)
