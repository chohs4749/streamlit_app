import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="서울시 주차장 검색", layout="wide")
st.title("🚗 서울시 공영주차장 검색")

uploaded_file = st.file_uploader("CSV 업로드(cp949)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="cp949")

    num_cols = ["기본 주차 요금","기본 주차 시간(분 단위)","추가 단위 요금",
                "추가 단위 시간(분 단위)","일 최대 요금","위도","경도"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",",""), errors="coerce")

    df["자치구"] = df["주소"].astype(str).str.extract(r"서울특별시\s+(\S+구)")

    
    gu = st.selectbox("자치구", ["전체"]+sorted(df["자치구"].dropna().unique().tolist()))
    kind = st.selectbox("주차장 종류", ["전체"]+sorted(df["주차장 종류명"].dropna().unique().tolist()))
    free = st.selectbox("유무료", ["전체"]+sorted(df["유무료구분명"].dropna().unique().tolist()))
    keyword = st.text_input("주차장명 검색")
    parking_time = st.slider("예상 주차시간(분)",30,720,120,30)

    f = df.copy()
    if gu!="전체": f=f[f["자치구"]==gu]
    if kind!="전체": f=f[f["주차장 종류명"]==kind]
    if free!="전체": f=f[f["유무료구분명"]==free]
    if keyword: f=f[f["주차장명"].str.contains(keyword,na=False)]

    def fee(r):
        if str(r["유무료구분명"]).strip()=="무료": return 0
        if pd.isna(r["기본 주차 요금"]): return None
        cost=r["기본 주차 요금"]
        bt=r["기본 주차 시간(분 단위)"]
        at=r["추가 단위 시간(분 단위)"]
        af=r["추가 단위 요금"]
        if parking_time>bt and pd.notna(at) and at>0:
            cost += math.ceil((parking_time-bt)/at)*af
        if pd.notna(r["일 최대 요금"]):
            cost=min(cost,r["일 최대 요금"])
        return int(cost)

    f["예상요금"]=f.apply(fee,axis=1)

    if not f.empty:
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=f["위도"].mean(),longitude=f["경도"].mean(),zoom=11),
            layers=[pdk.Layer("ScatterplotLayer",data=f,get_position="[경도, 위도]",get_radius=80,pickable=True)],
            tooltip={"text":"{주차장명}\n{주소}\n예상요금:{예상요금}원"}))

        cheap=f.dropna(subset=["예상요금"]).sort_values("예상요금")
        if not cheap.empty:
            b=cheap.iloc[0]
            st.success(f"가장 저렴한 주차장: {b['주차장명']}\n예상요금: {b['예상요금']:,}원")

        cols=[c for c in ["주차장명","주소","전화번호","주차장 종류명","유무료구분명","총 주차면","예상요금"] if c in f.columns]
        st.dataframe(f[cols].sort_values("예상요금"))
