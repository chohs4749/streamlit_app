import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="서울시 주차장 검색", layout="wide")

st.title("🚗 서울시 주차장 검색 서비스")

uploaded_file = st.file_uploader(
    "서울시 공영주차장 CSV 업로드",
    type="csv"
)

if uploaded_file is not None:

    # CP949 인코딩
    df = pd.read_csv(uploaded_file, encoding="cp949")

    # 숫자형 변환
    num_cols = [
        "기본 주차 요금",
        "기본 주차 시간(분 단위)",
        "추가 단위 요금",
        "추가 단위 시간(분 단위)",
        "일 최대 요금",
        "위도",
        "경도"
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["위도","경도"])

    # 자치구 추출
    df["자치구"] = df["주소"].str.split().str[1]

    col1, col2, col3 = st.columns(3)

    with col1:
        gu = st.selectbox(
            "자치구 선택",
            ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
        )

    with col2:
        kind = st.selectbox(
            "주차장 종류",
            ["전체"] + sorted(df["주차장 종류명"].dropna().unique().tolist())
        )

    with col3:
        pay = st.selectbox(
            "유무료",
            ["전체"] + sorted(df["유무료구분명"].dropna().unique().tolist())
        )

    parking_time = st.slider(
        "예상 주차시간(분)",
        30,
        720,
        120,
        step=30
    )

    filtered = df.copy()

    if gu != "전체":
        filtered = filtered[filtered["자치구"] == gu]

    if kind != "전체":
        filtered = filtered[filtered["주차장 종류명"] == kind]

    if pay != "전체":
        filtered = filtered[filtered["유무료구분명"] == pay]

    # 요금 계산 함수
    def calc_fee(row):

        if row["유무료구분명"] == "무료":
            return 0

        basic_fee = row["기본 주차 요금"]
        basic_time = row["기본 주차 시간(분 단위)"]
        add_fee = row["추가 단위 요금"]
        add_time = row["추가 단위 시간(분 단위)"]

        if pd.isna(basic_fee):
            return None

        fee = basic_fee

        if parking_time > basic_time and add_time > 0:
            extra = parking_time - basic_time
            fee += math.ceil(extra/add_time)*add_fee

        if pd.notna(row["일 최대 요금"]):
            fee = min(fee, row["일 최대 요금"])

        return int(fee)

    filtered["예상요금"] = filtered.apply(calc_fee, axis=1)

    st.subheader("📍 지도")

    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=filtered["위도"].mean(),
                longitude=filtered["경도"].mean(),
                zoom=11
            ),
            layers=[
                pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered,
                    get_position="[경도, 위도]",
                    get_radius=80,
                    pickable=True,
                    auto_highlight=True
                )
            ],
            tooltip={
                "text":
                "주차장 : {주차장명}\n"
                "주소 : {주소}\n"
                "예상요금 : {예상요금}원"
            }
        )
    )

    st.subheader("💰 가장 저렴한 주차장")

    cheapest = filtered.sort_values("예상요금").head(1)

    if len(cheapest):

        c = cheapest.iloc[0]

        st.success(
            f"""
            추천 주차장 : {c['주차장명']}

            주소 : {c['주소']}

            예상요금 : {c['예상요금']:,}원

            종류 : {c['주차장 종류명']}

            유무료 : {c['유무료구분명']}
            """
        )

    st.subheader("📋 검색 결과")

    st.dataframe(
        filtered[
            [
                "주차장명",
                "주소",
                "주차장 종류명",
                "유무료구분명",
                "예상요금",
                "기본 주차 요금",
                "일 최대 요금"
            ]
        ].sort_values("예상요금")
    )lumns.tolist())
