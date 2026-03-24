import streamlit as st
import googlemaps
import folium
from streamlit_folium import st_folium

# 1. Настройка на страницата
st.set_page_config(page_title="Транспортен Калкулатор", layout="wide", page_icon="🚚")

# 2. Извличане на защитени данни (Secrets)
try:
    API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
    # Проверка дали цената вече е зададена в сесията, ако не - взимаме я от Secrets
    if 'km_price' not in st.session_state:
        st.session_state.km_price = float(st.secrets.get("KM_PRICE", 1.50))
except Exception:
    st.error("⚠️ Грешка в конфигурацията! Моля, добавете GOOGLE_MAPS_API_KEY и ADMIN_PASSWORD в Settings -> Secrets на Streamlit Cloud.")
    st.stop()

gmaps = googlemaps.Client(key=API_KEY)

# 3. Странично меню
page = st.sidebar.radio("Меню", ["Калкулатор за търговци", "Админ Панел"])

# --- АДМИН ПАНЕЛ ---
if page == "Админ Панел":
    st.title("⚙️ Управление на цените (Админ)")
    pwd_input = st.text_input("Въведете парола за достъп", type="password")
    
    if pwd_input == ADMIN_PASSWORD:
        st.success("Достъпът е разрешен.")
        new_price = st.number_input("Текуща цена на километър (€):", value=st.session_state.km_price, step=0.01)
        if st.button("Запази новата цена"):
            st.session_state.km_price = new_price
            st.success(f"Цената е обновена на {new_price} €/км")
    elif pwd_input != "":
        st.error("Грешна парола!")

# --- КАЛКУЛАТОР ЗА ТЪРГОВЦИ ---
else:
    st.title("🚚 Изчисляване на транспорт до клиент")
    st.info(f"Актуална тарифа: **{st.session_state.km_price:.2f} €/км** (само отиване)")

    # Твоите точни координати на фабриката
    factory_coords = (42.57332743214374, 27.49522897860609) 
    
    customer_addr = st.text_input("Адрес на обекта:", placeholder="напр. София, бул. България 1")

    if st.button("Изчисли разстояние и цена"):
        if customer_addr:
            try:
                # Извличане на маршрут през пътната мрежа (Directions API)
                directions = gmaps.directions(factory_coords, customer_addr, mode="driving", language="bg")
                
                if not directions:
                    st.error("Не мога да намеря този адрес. Моля, проверете изписването.")
                else:
                    res = directions[0]
                    # Разстояние в километри
                    dist_km = res['legs'][0]['distance']['value'] / 1000
                    # Крайна цена (Разстояние * Цена на км)
                    total_euro = dist_km * st.session_state.km_price
                    
                    # Визуални резултати
                    col1, col2 = st.columns(2)
                    col1.metric("Пътно разстояние", f"{dist_km:.1f} км")
                    col2.metric("Обща цена (без ДДС)", f"{total_euro:.2f} €")
                    
                    # Декодиране на маршрута за картата
                    polyline_points = googlemaps.convert.decode_polyline(res['overview_polyline']['points'])
                    route_line = [[p['lat'], p['lng']] for p in polyline_points]
                    
                    # Създаване на картата
                    m = folium.Map(location=route_line[0], zoom_start=8)
                    
                    # Чертане на реалния път
                    folium.PolyLine(route_line, color="#1f77b4", weight=6, opacity=0.8).add_to(m)
                    
                    # Маркери за начало и край
                    folium.Marker(route_line[0], popup="Моята Фабрика", icon=folium.Icon(color='red', icon='industry', prefix='fa')).add_to(m)
                    folium.Marker(route_line[-1], popup="Клиент", icon=folium.Icon(color='green', icon='user', prefix='fa')).add_to(m)
                    
                    # Показване на картата
                    st_folium(m, width="100%", height=500, returned_objects=[])

            except Exception as e:
                st.error(f"Грешка при връзка с Google Maps: {e}")
        else:
            st.warning("Моля, въведете адрес на клиента.")
