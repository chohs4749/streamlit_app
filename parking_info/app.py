import streamlit as st
import pandas as pd
import pydeck as pdk

df = pd.read_csv(uploaded_file, encoding="cp949")

st.write(df.columns.tolist())

st.set_page_config(
    page_title="서울 주차장 정보",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울 주차장 정보 검색")

uploaded_file = st.file_uploader(
    "주차장 CSV 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    # cp949 인코딩
    df = pd.read_csv(uploaded_file, encoding="cp949")

    st.success("데이터 업로드 완료!")

    ############################
    # 사이드바
    ############################

    st.sidebar.header("검색 조건")

    gu = st.sidebar.selectbox(
        "자치구 선택",
        ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
    )

    parking_type = st.sidebar.selectbox(
        "주차장 종류",
        ["전체"] + sorted(df["주차장종류"].dropna().unique().tolist())
    )

    fee_type = st.sidebar.selectbox(
        "무료/유료",
        ["전체", "무료", "유료"]
    )

    parking_hour = st.sidebar.number_input(
        "예상 주차시간(시간)",
        min_value=0.5,
        max_value=24.0,
        value=2.0,
        step=0.5
    )

    ############################
    # 필터
    ############################

    filtered = df.copy()

    if gu != "전체":
        filtered = filtered[filtered["자치구"] == gu]

    if parking_type != "전체":
        filtered = filtered[filtered["주차장종류"] == parking_type]

    if fee_type != "전체":
        filtered = filtered[filtered["무료유료"] == fee_type]

    ############################
    # 요금 계산 함수
    ############################

    def calc_fee(row, hours):

        if row["무료유료"] == "무료":
            return 0

        minutes = hours * 60

        basic_time = row["기본시간"]
        basic_fee = row["기본요금"]

        if minutes <= basic_time:
            return basic_fee

        extra = minutes - basic_time

        unit = row["추가시간"]

        extra_fee = ((extra + unit - 1)//unit) * row["추가요금"]

        return basic_fee + extra_fee

    filtered["예상요금"] = filtered.apply(
        lambda x: calc_fee(x, parking_hour),
        axis=1
    )

    ############################
    # 가장 싼 주차장
    ############################

    if len(filtered) > 0:

        cheapest = filtered.loc[filtered["예상요금"].idxmin()]

        st.subheader("🏆 가장 저렴한 주차장")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "주차장",
            cheapest["주차장명"]
        )

        c2.metric(
            "예상요금",
            f'{int(cheapest["예상요금"]):,}원'
        )

        c3.metric(
            "자치구",
            cheapest["자치구"]
        )

    ############################
    # 지도
    ############################

    st.subheader("📍 주차장 위치")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position='[경도, 위도]',
        get_radius=60,
        get_fill_color='[255,0,0,160]',
        pickable=True
    )

    view = pdk.ViewState(
        latitude=filtered["위도"].mean(),
        longitude=filtered["경도"].mean(),
        zoom=11
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=view,
            layers=[layer],
            tooltip={
                "text":
                """
주차장 : {주차장명}
자치구 : {자치구}
종류 : {주차장종류}
예상요금 : {예상요금}원
                """
            }
        )
    )

    ############################
    # 표
    ############################

    st.subheader("주차장 목록")

    show = filtered[
        [
            "주차장명",
            "자치구",
            "주차장종류",
            "무료유료",
            "예상요금"
        ]
    ].sort_values("예상요금")

    st.dataframe(
        show,
        use_container_width=True
    )

else:

    st.info("CSV 파일을 업로드하세요.")
