import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium

# 1. Настройка на страницата
st.set_page_config(
    page_title="GEOTON | Транспортен Калкулатор", 
    layout="centered", 
    page_icon="🚚"
)

# Стилизиране с CSS за фирмени цветове (Синьо и Сиво)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-title {
        color: #004b87;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    div.stButton > button:first-child {
        background-color: #004b87;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ЛОГО И ЗАГЛАВИЕ
# Ако имаш файл logo.png в GitHub, той ще се зареди тук.
col_l, col_r = st.columns([1, 3])
with col_l:
    try:
        st.image("logo.png", width=120)
    except:
        st.subheader("🏗️ GEOTON")
with col_r:
    st.markdown("<h1 class='main-title'>Транспортен Калкулатор</h1>", unsafe_allow_html=True)

# 3. КОНФИГУРАЦИЯ (Secrets)
try:
    API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
except Exception:
    st.error("Грешка: Липсва Google Maps API Key в Settings -> Secrets!")
    st.stop()

gmaps = googlemaps.Client(key=API_KEY)

# 4. ПОЛЕТА ЗА ТЪРГОВЦИТЕ (На главната страница)
st.markdown("### 1. Настройки на курса")
col1, col2 = st.columns(2)

with col1:
    # Търговецът сам сменя цената тук
    km_price = st.number_input("Цена на километър (€):", value=1.50, step=0.05)

with col2:
    # Опция за празен курс (ако искаш да се смята отиване и връщане)
    round_trip = st.checkbox("Смятай отиване и връщане (x2)", value=False)

st.markdown("---")
st.markdown("### 2. Дестинация")
customer_addr = st.text_input("Въведете адрес на клиента:", placeholder="Град, улица, номер...")

# 5. ИЗЧИСЛЕНИЯ
if st.button("ИЗЧИСЛИ ТРАНСПОРТ"):
    if customer_addr:
        try:
            # Твоите координати
            factory_coords = (42.5749926, 27.4951604)
            
            directions = gmaps.directions(factory_coords, customer_addr, mode="driving", language="bg")
            
            if not directions:
                st.error("Адресът не е намерен! Моля, опитайте по-точно (напр. добавете град).")
            else:
                res = directions[0]
                dist_km = res['legs'][0]['distance']['value'] / 1000
                
                # Логика за умножение по 2, ако е отметнато "отиване и връщане"
                final_dist = dist_km * 2 if round_trip else dist_km
                total_cost = final_dist * km_price
                
                # Показване на резултати
                st.markdown("---")
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.metric("Общо километри", f"{final_dist:.1f} км")
                with res_col2:
                    st.metric("Крайна цена (без ДДС)", f"{total_cost:.2f} €")
                
                # КАРТА
                polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                route_line = [[p['lat'], p['lng']] for p in polyline_points]
                
                m = folium.Map(location=route_line[0], zoom_start=8)
                folium.PolyLine(route_line, color="#004b87", weight=6, opacity=0.8).add_to(m)
                
                # Маркери
                folium.Marker(route_line[0], popup="Геотон - Фабрика", icon=folium.Icon(color='blue', icon='industry', prefix='fa')).add_to(m)
                folium.Marker(route_line[-1], popup="Клиент", icon=folium.Icon(color='green', icon='user', prefix='fa')).add_to(m)
                
                st_folium(m, width="100%", height=400, returned_objects=[])
                
        except Exception as e:
            st.error(f"Грешка при връзка с Google: {e}")
    else:
        st.warning("Моля, първо въведете адрес.")

st.markdown("<br><p style='text-align: center; color: gray;'>© 2024 GEOTON Бургас</p>", unsafe_allow_html=True)
