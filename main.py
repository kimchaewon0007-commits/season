import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="사계절의 실종: 생물계절 변화 통계", page_icon="🦋", layout="wide"
)

# 자연 생태계 테마 CSS
st.markdown(
    """
    <style>
    .main { background-color: #f7fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
        color: #2d3748;
    }
    .stTabs [aria-selected="true"] {
        background-color: #276749 !important;
        color: white !important;
    }
    .metric-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #276749;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🦋 사계절의 실종: 기후변화에 따른 생물계절(Phenology) 통계")
st.markdown(
    "기온 상승이 국내 주요 동식물(제비, 매미, 벚꽃 등)의 **출현 시기 및 생활사(Life"
    " Cycle)**에 미치는 영향을 시계열 데이터로 분석합니다."
)

import numpy as np  # 맨 위에 없다면 추가

# 글로벌 다국가 데이터 생성 (한국 + 다른 나라들)
np.random.seed(42)
years = list(range(1995, 2026))
countries = ["South Korea", "Japan", "United States", "United Kingdom"]

data_list = []
for country in countries:
  shift_rate = 0.6 if country in ["South Korea", "Japan"] else 0.45
  temp_rate = 0.05 if country in ["South Korea", "Japan"] else 0.04

  for y in years:
    spring_day = 100 - (y - 1995) * shift_rate + np.random.normal(0, 2)
    avg_temp = 10.0 + (y - 1995) * temp_rate + np.random.normal(0, 0.3)
    data_list.append({
        "Year": y,
        "Country": country,
        "Spring_Event_Day": round(spring_day, 1),
        "Avg_Temperature": round(avg_temp, 2),
    })

df_global = pd.DataFrame(data_list)
# 탭 메뉴 구성
tab1, tab2, tab3 = st.tabs([
    "📈 종별 출현일 변화 시계열 분석",
    "🌡️ 기온 상승과의 상관관계",
    "📋 데이터 원본 및 통계 요약",
])

with tab1:
  st.subheader("연도별 생물계절 관측 시계열 통계")
  st.markdown(
      "과거 30년 동안 봄철 생물들의 등장 시기가 얼마나 앞당겨졌는지 확인합니다."
      " (값이 작을수록 더 이른 시기에 출현함을 의미합니다)"
  )

  # 사용자 선택 박스
  target_spec = st.selectbox(
      "분석할 생물종을 선택하세요:",
      [
          "제비 첫 도래일 (봄철 이동성 조류)",
          "벚꽃 개화일 (식물계절)",
          "매미 첫 울음소리 (여름철 곤충)",
      ],
  )

  if "제비" in target_spec:
    y_col = "Swallow_Arrival_Day"
    title_text = "연도별 제비 첫 도래일 추이 (빨라질수록 봄이 빨라짐)"
    line_color = "#3182ce"
  elif "벚꽃" in target_spec:
    y_col = "Cherry_Blossom_Day"
    title_text = "연도별 벚꽃 개화일 추이 (점차 빨라지는 개화)"
    line_color = "#e53e3e"
  else:
    y_col = "Cicada_Cry_Day"
    title_text = "연도별 매미 첫 울음소리 관측일 추이"
    line_color = "#d69e2e"

  # Plotly 시계열 선 그래프 (추세선 포함)
  fig_trend = px.scatter(
      df_phenology,
      x="Year",
      y=y_col,
      trendline="ols",
      labels={"Year": "연도", y_col: "1월 1일 기준 경과일 (Day)"},
      title=title_text,
  )
  fig_trend.update_traces(marker=dict(size=8), line=dict(width=3))
  st.plotly_chart(fig_trend, use_container_width=True)

  st.info(
      "💡 **생태학적 인사이트:** 추세선(Trendline)의 기울기가 음수(-)를"
      " 나타낸다는 것은, 매년 기후 온난화로 인해 생물의 출현 시기가 평균적으로"
      " 빨라지고 있음을 통계적으로 증명합니다."
  )

with tab2:
  st.subheader("🌡️ 봄철 평균 기온과 생물 출현일의 관계")
  st.markdown(
      "지구과학적 지표인 **'연평균 기온'**과 생물학적 지표인 **'출현 시기'**를"
      " 교차 분석합니다."
  )

  # 가상의 기온 상승 데이터 결합
  df_phenology["Avg_Temp"] = [
      12.0 + (y - 1995) * 0.05 + (y % 5) * 0.1 for y in years
  ]

  fig_scatter = px.scatter(
      df_phenology,
      x="Avg_Temp",
      y="Cherry_Blossom_Day",
      color="Year",
      labels={
          "Avg_Temp": "연평균 기온 (°C)",
          "Cherry_Blossom_Day": "벚꽃 개화일 (Day)",
      },
      title="연평균 기온 상승에 따른 벚꽃 개화일 단축 효과",
      color_continuous_scale="Viridis",
  )
  st.plotly_chart(fig_scatter, use_container_width=True)

  st.markdown(
      """
        <div class="metric-box">
        <h4>🌍 지구과학-생명과학 융합 포인트</h4>
        <p>기온이 1°C 상승할 때마다 식물의 개화 시기와 철새의 이동 시기가 며칠씩 앞당겨지는지 
        상관계수(Correlation)를 도출함으로써, 기후변화가 생태계의 불일치(Mismatch) 현상을 
        어떻게 유발하는지 정량적으로 설명할 수 있습니다.</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

with tab3:
  st.subheader("📋 생물계절 통계 원본 데이터")
  st.dataframe(df_phenology, use_container_width=True)

  # CSV 다운로드 버튼 제공 (포트폴리오 완성도 향상)
  csv_data = df_phenology.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 통계 데이터셋 다운로드 (CSV)",
      data=csv_data,
      file_name="phenology_climate_data.csv",
      mime="text/csv",
  )
