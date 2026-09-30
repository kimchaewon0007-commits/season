import streamlit as st
import pandas as pd
import numpy as np
import requests
from sklearn.linear_model import LinearRegression


# ============================================================
# 페이지 설정
# ============================================================

st.set_page_config(
    page_title="Global Environment Explorer",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# 도시 정보
# ============================================================

CITIES = {
    "대한민국": {
        "서울": {"lat": 37.5665, "lon": 126.9780, "station": "47108"},
        "부산": {"lat": 35.1796, "lon": 129.0756, "station": "47159"},
        "대전": {"lat": 36.3504, "lon": 127.3845, "station": "47133"},
        "대구": {"lat": 35.8714, "lon": 128.6014, "station": "47142"},
        "광주": {"lat": 35.1595, "lon": 126.8526, "station": "47158"},
        "제주": {"lat": 33.4996, "lon": 126.5312, "station": "47185"},
        "전주": {"lat": 35.8242, "lon": 127.1480, "station": "47146"},
        "강릉": {"lat": 37.7519, "lon": 128.8761, "station": "47105"},
        "여수": {"lat": 34.7604, "lon": 127.6622, "station": "47168"}
    },

    "일본": {
        "도쿄": {"lat": 35.6762, "lon": 139.6503, "station": "47662"},
        "오사카": {"lat": 34.6937, "lon": 135.5023, "station": "47772"},
        "교토": {"lat": 35.0116, "lon": 135.7681, "station": "47759"},
        "삿포로": {"lat": 43.0618, "lon": 141.3545, "station": "47412"},
        "후쿠오카": {"lat": 33.5904, "lon": 130.4017, "station": "47807"}
    },

    "미국": {
        "뉴욕": {"lat": 40.7128, "lon": -74.0060, "station": "72503"},
        "로스앤젤레스": {"lat": 34.0522, "lon": -118.2437, "station": "72295"},
        "시카고": {"lat": 41.8781, "lon": -87.6298, "station": "72530"},
        "시애틀": {"lat": 47.6062, "lon": -122.3321, "station": "72793"},
        "보스턴": {"lat": 42.3601, "lon": -71.0589, "station": "72509"}
    },

    "영국": {
        "런던": {"lat": 51.5074, "lon": -0.1278, "station": "03772"},
        "맨체스터": {"lat": 53.4808, "lon": -2.2426, "station": "03334"},
        "버밍엄": {"lat": 52.4862, "lon": -1.8904, "station": "03354"}
    },

    "프랑스": {
        "파리": {"lat": 48.8566, "lon": 2.3522, "station": "07149"},
        "리옹": {"lat": 45.7640, "lon": 4.8357, "station": "07481"},
        "니스": {"lat": 43.7102, "lon": 7.2620, "station": "07690"}
    },

    "독일": {
        "베를린": {"lat": 52.5200, "lon": 13.4050, "station": "10384"},
        "뮌헨": {"lat": 48.1351, "lon": 11.5820, "station": "10866"},
        "함부르크": {"lat": 53.5511, "lon": 9.9937, "station": "10147"}
    },

    "호주": {
        "시드니": {"lat": -33.8688, "lon": 151.2093, "station": "94767"},
        "멜버른": {"lat": -37.8136, "lon": 144.9631, "station": "94866"},
        "브리즈번": {"lat": -27.4698, "lon": 153.0251, "station": "94576"}
    }
}


# ============================================================
# 환경 항목
# ============================================================

ENVIRONMENT_ITEMS = [
    "평균 기온",
    "강수량",
    "환경오염",
    "CO₂ 배출량",
    "생태계 다양성"
]


# ============================================================
# 제목
# ============================================================

st.title("🌍 Global Environment Explorer")

st.write(
    "세계 여러 지역의 기후, 환경오염, 탄소배출 및 "
    "생태계 변화를 통계와 그래프로 확인할 수 있습니다."
)

st.divider()


# ============================================================
# 사용자 선택
# ============================================================

st.sidebar.header("분석 설정")

country = st.sidebar.selectbox(
    "국가",
    list(CITIES.keys())
)

city = st.sidebar.selectbox(
    "도시",
    list(CITIES[country].keys())
)

item = st.sidebar.selectbox(
    "분석 항목",
    ENVIRONMENT_ITEMS
)

city_info = CITIES[country][city]


# ============================================================
# 분석 기간
# ============================================================

st.sidebar.subheader("기간")

start_year = st.sidebar.number_input(
    "시작 연도",
    min_value=1930,
    max_value=2026,
    value=1930
)

end_year = st.sidebar.number_input(
    "종료 연도",
    min_value=1930,
    max_value=2026,
    value=2026
)

if start_year >= end_year:
    st.error("종료 연도는 시작 연도보다 커야 합니다.")
    st.stop()


# ============================================================
# 미래 예측
# ============================================================

st.sidebar.subheader("미래 예측")

prediction_year = st.sidebar.slider(
    "예측 종료 연도",
    min_value=2027,
    max_value=2100,
    value=2050
)


# ============================================================
# Meteostat 연간 기후 데이터
# ============================================================

@st.cache_data(ttl=86400)
def get_meteostat_data(station_id):

    url = (
        "https://bulk.meteostat.net/v2/"
        "daily/"
    )

    # Meteostat Python API 대신 공개 데이터 구조를
    # 사용하는 경우를 대비해 빈 결과를 반환
    # 실제 운영에서는 station별 데이터를 가져오도록 확장 가능
    return pd.DataFrame()


# ============================================================
# World Bank Climate API
# ============================================================

@st.cache_data(ttl=86400)
def get_world_bank_climate(country_code):

    variable = "tas"

    url = (
        "https://cckpapi.worldbank.org/"
        "cckp/v1/"
        "cru-x0.5_timeseries_"
        "tas_annual_1901-2024_"
        "median_historical_ensemble_all_mean/"
        f"{country_code}?_format=json"
    )

    try:
        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:
            return pd.DataFrame()

        data = response.json()

        rows = []

        # API 응답 구조가 바뀌더라도
        # 가능한 경우 데이터를 추출
        if isinstance(data, dict):

            for key, value in data.items():

                if isinstance(value, (int, float)):

                    try:
                        year = int(key)

                        if 1901 <= year <= 2024:
                            rows.append({
                                "연도": year,
                                "값": value
                            })

                    except:
                        pass

        return pd.DataFrame(rows)

    except Exception:
        return pd.DataFrame()


# ============================================================
# Our World in Data CO2
# ============================================================

@st.cache_data(ttl=86400)
def get_co2_data():

    url = (
        "https://ourworldindata.org/"
        "grapher/annual-co2-emissions-per-country.csv"
        "?v=1&csvType=full&useColumnShortNames=false"
    )

    try:

        df = pd.read_csv(
            url,
            storage_options={
                "User-Agent":
                "Global Environment Explorer"
            }
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# 환경오염 데이터
# ============================================================

@st.cache_data(ttl=86400)
def get_air_pollution_data():

    # WHO 공식 데이터 페이지에서 제공되는
    # 도시별 연평균 PM2.5 / PM10 / NO2 자료를
    # 실제 데이터 파일로 연결할 수 있도록 구성
    #
    # WHO 데이터는 2010~2024년 범위를 제공하며
    # 모든 도시가 모든 연도에 존재하는 것은 아님.

    return pd.DataFrame()


# ============================================================
# 생태계 다양성
# ============================================================

@st.cache_data(ttl=86400)
def get_red_list_index():

    url = (
        "https://ourworldindata.org/"
        "grapher/red-list-index.csv"
    )

    try:

        df = pd.read_csv(
            url,
            storage_options={
                "User-Agent":
                "Global Environment Explorer"
            }
        )

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# 미래 예측
# ============================================================

def predict_future(data, final_year):

    data = data.dropna()

    if len(data) < 10:
        return pd.DataFrame()

    X = data[["연도"]]
    y = data["값"]

    model = LinearRegression()

    model.fit(X, y)

    last_year = int(data["연도"].max())

    future_years = np.arange(
        last_year + 1,
        final_year + 1
    )

    if len(future_years) == 0:
        return pd.DataFrame()

    predictions = model.predict(
        future_years.reshape(-1, 1)
    )

    return pd.DataFrame({
        "연도": future_years,
        "예측값": predictions
    })


# ============================================================
# 평균 기온
# ============================================================

if item == "평균 기온":

    st.header(f"🌡️ {city} 평균 기온")

    st.info(
        "기온 자료는 실제 관측·재구성 기후자료를 이용합니다. "
        "도시별 이용 가능한 시작 연도는 서로 다를 수 있습니다."
    )

    st.write(
        "World Bank Climate Change Knowledge Portal은 "
        "CRU 기반 역사 기후자료를 제공하며, "
        "역사 자료는 1901년부터 제공됩니다."
    )

    # 국가별 ISO 코드
    country_codes = {
        "대한민국": "KOR",
        "일본": "JPN",
        "미국": "USA",
        "영국": "GBR",
        "프랑스": "FRA",
        "독일": "DEU",
        "호주": "AUS"
    }

    code = country_codes[country]

    climate_df = get_world_bank_climate(code)

    if not climate_df.empty:

        climate_df = climate_df[
            (climate_df["연도"] >= start_year)
            & (climate_df["연도"] <= end_year)
        ]

        if not climate_df.empty:

            st.subheader("연도별 기온 변화")

            st.line_chart(
                climate_df.set_index("연도")["값"]
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "평균",
                f"{climate_df['값'].mean():.2f}"
            )

            col2.metric(
                "최고",
                f"{climate_df['값'].max():.2f}"
            )

            col3.metric(
                "최저",
                f"{climate_df['값'].min():.2f}"
            )

            prediction_data = climate_df.copy()

            prediction = predict_future(
                prediction_data,
                prediction_year
            )

            if not prediction.empty:

                st.subheader("🔮 미래 예측")

                combined = pd.concat([
                    climate_df.rename(
                        columns={"값": "관측값"}
                    ).set_index("연도"),
                    prediction.set_index("연도")
                ])

                st.line_chart(
                    combined
                )

                st.caption(
                    "예측값은 과거 자료에 선형회귀를 적용한 "
                    "모델 추정치이며 실제 관측값이 아닙니다."
                )

        else:

            st.warning(
                "선택한 기간에 사용할 수 있는 자료가 없습니다."
            )

    else:

        st.warning(
            "현재 연결된 기후 데이터에서 자료를 불러오지 못했습니다."
        )


# ============================================================
# CO2
# ============================================================

elif item == "CO₂ 배출량":

    st.header(f"🏭 {country} CO₂ 배출량")

    co2 = get_co2_data()

    if not co2.empty:

        country_data = co2[
            co2["Entity"] == country
        ].copy()

        if not country_data.empty:

            year_column = "Year"

            value_columns = [
                column
                for column in country_data.columns
                if "Annual CO₂ emissions" in column
            ]

            if value_columns:

                value_column = value_columns[0]

                country_data = country_data[
                    (country_data[year_column] >= start_year)
                    & (country_data[year_column] <= end_year)
                ]

                country_data = country_data[
                    [year_column, value_column]
                ].dropna()

                country_data.columns = [
                    "연도",
                    "CO2 배출량"
                ]

                st.line_chart(
                    country_data.set_index("연도")
                )

                col1, col2 = st.columns(2)

                col1.metric(
                    "평균 연간 배출량",
                    f"{country_data['CO2 배출량'].mean():,.0f} t"
                )

                col2.metric(
                    "최근 자료",
                    f"{country_data['CO2 배출량'].iloc[-1]:,.0f} t"
                )

                st.dataframe(
                    country_data,
                    use_container_width=True,
                    hide_index=True
                )

    st.caption(
        "자료: Our World in Data / Global Carbon Budget"
    )


# ============================================================
# 생태계 다양성
# ============================================================

elif item == "생태계 다양성":

    st.header(f"🌱 {country} 생태계 다양성")

    biodiversity = get_red_list_index()

    if not biodiversity.empty:

        country_data = biodiversity[
            biodiversity["Entity"] == country
        ].copy()

        if not country_data.empty:

            year_columns = [
                c for c in country_data.columns
                if c.lower() in [
                    "year",
                    "red list index"
                ]
            ]

            if len(year_columns) >= 2:

                year_col = [
                    c for c in year_columns
                    if c.lower() == "year"
                ][0]

                value_col = [
                    c for c in year_columns
                    if c.lower() != "year"
                ][0]

                country_data = country_data[
                    (country_data[year_col] >= start_year)
                    & (country_data[year_col] <= end_year)
                ]

                country_data = country_data[
                    [year_col, value_col]
                ].dropna()

                country_data.columns = [
                    "연도",
                    "생태계 다양성 지표"
                ]

                if not country_data.empty:

                    st.line_chart(
                        country_data.set_index("연도")
                    )

                    st.metric(
                        "최근 Red List Index",
                        f"{country_data['생태계 다양성 지표'].iloc[-1]:.3f}"
                    )

                    st.dataframe(
                        country_data,
                        use_container_width=True,
                        hide_index=True
                    )

    st.caption(
        "자료: BirdLife International / IUCN Red List Index"
    )


# ============================================================
# 환경오염
# ============================================================

elif item == "환경오염":

    st.header(f"🌫️ {city} 환경오염")

    st.info(
        "도시 대기질 자료는 WHO Ambient Air Quality Database를 "
        "기준으로 연결할 수 있습니다."
    )

    st.write(
        "WHO 자료에는 도시·정착지별 PM2.5, PM10, NO₂ "
        "연평균 농도가 포함되어 있습니다."
    )

    st.warning(
        "대기오염 자료는 1930년부터 매년 존재하는 자료가 아닙니다. "
        "자료가 존재하는 연도만 표시해야 하며, "
        "없는 과거값을 임의로 만들어서는 안 됩니다."
    )

    st.link_button(
        "WHO 대기질 데이터 확인",
        "https://www.who.int/data/gho/data/themes/air-pollution/who-air-quality-database"
    )


# ============================================================
# 기본 정보
# ============================================================

st.divider()

st.subheader("📊 데이터 안내")

st.write(
    f"""
    **선택 지역:** {country} · {city}

    **분석 항목:** {item}

    **선택 기간:** {start_year}~{end_year}

    **미래 예측:** {prediction_year}년까지

    데이터가 실제로 존재하지 않는 연도는 임의의 숫자로
    채우지 않고 빈 값으로 처리합니다.
    """
)

st.caption(
    "환경·기후 데이터는 자료 제공기관의 갱신 및 수정에 따라 "
    "변경될 수 있습니다."
)
