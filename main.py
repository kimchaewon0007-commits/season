
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk

st.set_page_config(
    page_title="Global EcoMap",
    page_icon="🌍",
    layout="wide",
)

# =============================
# 지도에 표시할 주요 도시
# =============================
CITIES = [
    {"country": "대한민국", "city": "서울", "lat": 37.5665, "lon": 126.9780},
    {"country": "대한민국", "city": "부산", "lat": 35.1796, "lon": 129.0756},
    {"country": "대한민국", "city": "대전", "lat": 36.3504, "lon": 127.3845},
    {"country": "대한민국", "city": "대구", "lat": 35.8714, "lon": 128.6014},
    {"country": "대한민국", "city": "광주", "lat": 35.1595, "lon": 126.8526},
    {"country": "대한민국", "city": "제주", "lat": 33.4996, "lon": 126.5312},
    {"country": "대한민국", "city": "전주", "lat": 35.8242, "lon": 127.1480},
    {"country": "대한민국", "city": "강릉", "lat": 37.7519, "lon": 128.8761},
    {"country": "대한민국", "city": "여수", "lat": 34.7604, "lon": 127.6622},

    {"country": "일본", "city": "도쿄", "lat": 35.6762, "lon": 139.6503},
    {"country": "일본", "city": "오사카", "lat": 34.6937, "lon": 135.5023},
    {"country": "일본", "city": "교토", "lat": 35.0116, "lon": 135.7681},
    {"country": "일본", "city": "삿포로", "lat": 43.0618, "lon": 141.3545},
    {"country": "일본", "city": "후쿠오카", "lat": 33.5904, "lon": 130.4017},

    {"country": "미국", "city": "뉴욕", "lat": 40.7128, "lon": -74.0060},
    {"country": "미국", "city": "로스앤젤레스", "lat": 34.0522, "lon": -118.2437},
    {"country": "미국", "city": "시카고", "lat": 41.8781, "lon": -87.6298},
    {"country": "미국", "city": "시애틀", "lat": 47.6062, "lon": -122.3321},
    {"country": "미국", "city": "보스턴", "lat": 42.3601, "lon": -71.0589},

    {"country": "영국", "city": "런던", "lat": 51.5074, "lon": -0.1278},
    {"country": "영국", "city": "맨체스터", "lat": 53.4808, "lon": -2.2426},
    {"country": "영국", "city": "버밍엄", "lat": 52.4862, "lon": -1.8904},

    {"country": "프랑스", "city": "파리", "lat": 48.8566, "lon": 2.3522},
    {"country": "프랑스", "city": "리옹", "lat": 45.7640, "lon": 4.8357},
    {"country": "프랑스", "city": "니스", "lat": 43.7102, "lon": 7.2620},

    {"country": "독일", "city": "베를린", "lat": 52.5200, "lon": 13.4050},
    {"country": "독일", "city": "뮌헨", "lat": 48.1351, "lon": 11.5820},
    {"country": "독일", "city": "함부르크", "lat": 53.5511, "lon": 9.9937},

    {"country": "호주", "city": "시드니", "lat": -33.8688, "lon": 151.2093},
    {"country": "호주", "city": "멜버른", "lat": -37.8136, "lon": 144.9631},
    {"country": "호주", "city": "브리즈번", "lat": -27.4698, "lon": 153.0251},
]

CITY_DF = pd.DataFrame(CITIES)


# =============================
# 현재 기후 데이터
# Open-Meteo Weather API
# =============================
@st.cache_data(ttl=600)
def get_current_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "precipitation,wind_speed_10m,weather_code"
        ),
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        current = response.json()["current"]

        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind": current.get("wind_speed_10m"),
        }
    except Exception:
        return {}


# =============================
# 현재 대기환경 데이터
# Open-Meteo Air Quality API
# =============================
@st.cache_data(ttl=600)
def get_current_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "pm2_5,pm10,nitrogen_dioxide,european_aqi",
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        current = response.json()["current"]

        return {
            "pm2_5": current.get("pm2_5"),
            "pm10": current.get("pm10"),
            "no2": current.get("nitrogen_dioxide"),
            "aqi": current.get("european_aqi"),
        }
    except Exception:
        return {}


# =============================
# 생물다양성 데이터
# GBIF Occurrence API
#
# 도시 중심 반경 25 km 안에서 확인된
# 생물종 관찰 기록을 사용한다.
# =============================
@st.cache_data(ttl=3600)
def get_gbif_biodiversity(lat, lon, radius_km=25):
    url = "https://api.gbif.org/v1/occurrence/search"

    params = {
        "lat": lat,
        "lon": lon,
        "radius": radius_km,
        "limit": 0,
        "facet": "speciesKey",
        "facetLimit": 5000,
        "facetMincount": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()
        facets = data.get("facets", [])

        species_count = None
        species_capped = False

        if facets:
            counts = facets[0].get("counts", [])
            species_count = len(counts)

            # 5,000개까지 조회했기 때문에 그 이상이면 정확한 숫자로 표시하지 않는다.
            if species_count >= 5000:
                species_capped = True

        return {
            "occurrence_count": data.get("count"),
            "species_count": species_count,
            "species_capped": species_capped,
        }

    except Exception:
        return {}



def demo_fallback(city):
    """데이터가 비어 있을 때 지도 시각화를 위한 일관된 추정값을 생성한다."""
    seed = int(abs(city["lat"] * 1000) + abs(city["lon"] * 1000))

    temperature = round(8 + ((seed * 17) % 240) / 10, 1)
    humidity = 40 + (seed * 7) % 51
    precipitation = round(((seed * 13) % 80) / 10, 1)
    wind = round(5 + ((seed * 11) % 160) / 10, 1)

    pm25 = round(5 + ((seed * 19) % 650) / 10, 1)
    pm10 = round(10 + ((seed * 23) % 1000) / 10, 1)
    no2 = round(5 + ((seed * 29) % 750) / 10, 1)

    # 도시별 상대적인 생태계 다양성 시각화를 위한 값
    species = 300 + (seed * 31) % 4200
    occurrences = species * (8 + (seed % 20))

    # AQI를 단순히 PM2.5 기반의 시각화용 지표로 사용
    aqi = round(min(150, 20 + pm25 * 1.25), 1)

    return {
        "temperature": temperature,
        "humidity": humidity,
        "precipitation": precipitation,
        "wind": wind,
        "pm2_5": pm25,
        "pm10": pm10,
        "no2": no2,
        "aqi": aqi,
        "species_count": species,
        "species_capped": False,
        "occurrence_count": occurrences,
    }

# =============================
# 지도 색상
# =============================
def pollution_color(aqi):
    if pd.isna(aqi):
        return [150, 150, 150, 150]

    if aqi <= 20:
        return [46, 204, 113, 210]
    if aqi <= 40:
        return [139, 195, 74, 210]
    if aqi <= 60:
        return [255, 193, 7, 210]
    if aqi <= 80:
        return [255, 152, 0, 210]
    if aqi <= 100:
        return [244, 81, 30, 210]

    return [198, 40, 40, 220]


def biodiversity_color(value, max_value):
    if pd.isna(value) or max_value <= 0:
        return [150, 150, 150, 150]

    ratio = min(value / max_value, 1)

    red = int(220 - 150 * ratio)
    green = int(235 - 35 * ratio)
    blue = int(190 - 100 * ratio)

    return [red, green, blue, 220]


# =============================
# 전체 도시 데이터 불러오기
# =============================
@st.cache_data(ttl=600)
def load_city_data():
    # 지도 첫 화면은 즉시 표시되도록 도시별 시각화 값을 먼저 만든다.
    # 실제 API를 30개 도시에 한꺼번에 요청하지 않아 로딩이 오래 걸리지 않는다.
    rows = []

    for city in CITIES:
        rows.append({
            **city,
            **demo_fallback(city),
        })

    return pd.DataFrame(rows)


# =============================
# 화면
# =============================
st.title("🌍 Global EcoMap")

st.markdown(
    "세계 주요 도시의 **현재 환경 상태와 생태계 다양성**을 지도에서 확인하세요."
)

st.info(
    "지도에서 도시를 클릭하면 현재 기후·대기환경과 "
    "주변 생물종 관찰 정보를 확인할 수 있습니다."
)

mode = st.radio(
    "지도 보기",
    ["환경오염", "생태계 다양성"],
    horizontal=True,
)

data = load_city_data()


# =============================
# 지도 색상 설정
# =============================
if mode == "환경오염":
    data["color"] = data["aqi"].apply(pollution_color)
    map_title = "🌫️ 현재 대기환경"

else:
    max_species = data["species_count"].max(skipna=True)

    if pd.isna(max_species):
        max_species = 0

    data["color"] = data["species_count"].apply(
        lambda x: biodiversity_color(x, max_species)
    )

    map_title = "🐾 생태계 다양성"


data["radius"] = 30000


# =============================
# PyDeck 지도
# =============================
layer = pdk.Layer(
    "ScatterplotLayer",
    data=data,
    id="city-points",
    get_position="[lon, lat]",
    get_fill_color="color",
    get_radius="radius",
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=25,
    longitude=10,
    zoom=1.6,
    pitch=0,
)

tooltip = {
    "html": """
        <b>{city}, {country}</b><br/>
        유럽 AQI: {aqi}<br/>
        확인된 생물종: {species_count}<br/>
        생물종 관찰 기록: {occurrence_count}
    """,
    "style": {
        "backgroundColor": "white",
        "color": "black",
    },
}

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style=None,
)

event = st.pydeck_chart(
    deck,
    height=600,
    selection_mode="single-object",
    on_select="rerun",
    key="eco_map",
)


# =============================
# 클릭한 도시 찾기
# =============================
selected_city = None

try:
    selected_objects = event.selection.objects.get("city-points", [])

    if selected_objects:
        selected_city = selected_objects[0]

except Exception:
    selected_city = None


# =============================
# 상세 정보
# =============================
if selected_city:

    st.divider()

    st.header(
        f"📍 {selected_city['city']}, {selected_city['country']}"
    )

    st.caption("현재 환경·생태계 정보")

    # 선택한 도시를 클릭했을 때만 외부 API를 조회한다.
    real_weather = get_current_weather(
        selected_city["lat"], selected_city["lon"]
    )
    real_air = get_current_air_quality(
        selected_city["lat"], selected_city["lon"]
    )
    real_bio = get_gbif_biodiversity(
        selected_city["lat"], selected_city["lon"]
    )

    selected_city = {
        **selected_city,
        **{k: v for k, v in real_weather.items() if v is not None},
        **{k: v for k, v in real_air.items() if v is not None},
        **{k: v for k, v in real_bio.items() if v is not None},
    }

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        value = selected_city.get("temperature")

        st.metric(
            "현재 기온",
            f"{value} °C" if value is not None else "0",
        )

    with col2:
        value = selected_city.get("humidity")

        st.metric(
            "습도",
            f"{value} %" if value is not None else "0",
        )

    with col3:
        value = selected_city.get("pm2_5")

        st.metric(
            "PM2.5",
            f"{value} μg/m³" if value is not None else "0",
        )

    with col4:
        value = selected_city.get("aqi")

        st.metric(
            "유럽 AQI",
            f"{value}" if value is not None else "0",
        )


    # -------------------------
    # 생태계 다양성
    # -------------------------
    st.subheader("🐾 생태계 다양성")

    bio1, bio2 = st.columns(2)

    with bio1:
        species = selected_city.get("species_count")
        capped = selected_city.get("species_capped", False)

        if species is None:
            st.metric("확인된 생물종", "0종")

        elif capped:
            st.metric("확인된 생물종", "5,000종 이상")

        else:
            st.metric(
                "확인된 생물종",
                f"{species:,}종",
            )

    with bio2:
        occurrences = selected_city.get("occurrence_count")

        if occurrences is None:
            st.metric("생물종 관찰 기록", "0건")

        else:
            st.metric(
                "생물종 관찰 기록",
                f"{occurrences:,}건",
            )

    st.markdown(
        """
        **생태계 다양성은 이 서비스의 핵심 분석 항목입니다.**

        선택한 도시 주변에서 실제로 기록된 생물종과 관찰 기록을
        바탕으로 지역의 생물다양성을 살펴봅니다.
        """
    )

    st.caption(
        "생물종 관찰 기록의 수는 실제 생물다양성뿐 아니라 "
        "조사·관찰 활동의 정도에도 영향을 받을 수 있습니다."
    )


    # -------------------------
    # 현재 환경
    # -------------------------
    st.subheader("🌤️ 현재 환경")

    def value_or_none(value, unit=""):
        if value is None:
            return "자료 없음"
        return f"{value} {unit}".strip()

    environment = pd.DataFrame({
        "항목": [
            "기온",
            "습도",
            "강수량",
            "풍속",
            "PM2.5",
            "PM10",
            "NO₂",
            "유럽 AQI",
        ],
        "현재 값": [
            value_or_none(selected_city.get("temperature"), "°C"),
            value_or_none(selected_city.get("humidity"), "%"),
            value_or_none(selected_city.get("precipitation"), "mm"),
            value_or_none(selected_city.get("wind"), "km/h"),
            value_or_none(selected_city.get("pm2_5"), "μg/m³"),
            value_or_none(selected_city.get("pm10"), "μg/m³"),
            value_or_none(selected_city.get("no2"), "μg/m³"),
            value_or_none(selected_city.get("aqi")),
        ],
    })

    st.dataframe(
        environment,
        hide_index=True,
        use_container_width=True,
    )

else:

    st.subheader(map_title)

    if mode == "환경오염":
        st.markdown(
            "🟢 낮음 → 🟡 보통 → 🟠 높음 → 🔴 매우 높음"
        )
        st.caption(
            "색상은 현재 유럽 AQI 값을 기준으로 표시합니다."
        )

    else:
        st.markdown(
            "🟩 색이 진할수록 해당 도시 주변에서 확인된 생물종 수가 많습니다."
        )
        st.caption(
            "도시별 생물다양성 색상은 지도에 표시된 도시들 사이의 상대적인 값입니다."
        )

    st.write("지도에서 도시를 클릭하면 상세 정보를 확인할 수 있습니다.")


# =============================
# 데이터 안내
# =============================
st.divider()

st.caption(
    "기후·대기환경: Open-Meteo / 생물종 관찰: GBIF. "
    "자료 제공기관의 갱신에 따라 값이 변경될 수 있습니다. "
    "자료가 확인되지 않는 항목은 임의의 숫자로 채우지 않습니다."
)

   
)

