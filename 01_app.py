import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="🍽️ 날씨별 음식 추천",
    page_icon="🍜",
    layout="centered"
)

st.title("🌤️ 오늘 날씨에 따른 음식 추천")
st.write("오늘 날씨를 선택하면 어울리는 음식을 추천해드립니다!")

# 음식 데이터
foods = {
    "맑음": {
        "name": "비빔밥",
        "image": "images/bibimbap.jpg",
        "calorie": "560 kcal",
        "nutrition": {
            "탄수화물": "75 g",
            "단백질": "20 g",
            "지방": "15 g"
        },
        "reason": "화창한 날에는 신선한 채소가 가득한 비빔밥!"
    },

    "비": {
        "name": "김치찌개",
        "image": "images/kimchi_jjigae.jpg",
        "calorie": "480 kcal",
        "nutrition": {
            "탄수화물": "30 g",
            "단백질": "28 g",
            "지방": "20 g"
        },
        "reason": "비 오는 날에는 얼큰한 국물이 최고!"
    },

    "눈": {
        "name": "라면",
        "image": "images/ramen.jpg",
        "calorie": "520 kcal",
        "nutrition": {
            "탄수화물": "70 g",
            "단백질": "12 g",
            "지방": "18 g"
        },
        "reason": "눈 오는 날에는 따뜻한 라면 한 그릇!"
    },

    "흐림": {
        "name": "파스타",
        "image": "images/pasta.jpg",
        "calorie": "650 kcal",
        "nutrition": {
            "탄수화물": "80 g",
            "단백질": "18 g",
            "지방": "22 g"
        },
        "reason": "기분 전환엔 크림 파스타!"
    },

    "더움": {
        "name": "냉면",
        "image": "images/naengmyeon.jpg",
        "calorie": "430 kcal",
        "nutrition": {
            "탄수화물": "72 g",
            "단백질": "13 g",
            "지방": "4 g"
        },
        "reason": "더운 날에는 시원한 냉면!"
    },

    "추움": {
        "name": "삼계탕",
        "image": "images/samgyetang.jpg",
        "calorie": "920 kcal",
        "nutrition": {
            "탄수화물": "40 g",
            "단백질": "55 g",
            "지방": "35 g"
        },
        "reason": "추운 날에는 몸보신 삼계탕!"
    }
}

weather = st.selectbox(
    "오늘 날씨를 선택하세요",
    list(foods.keys())
)

if st.button("🍴 음식 추천받기"):

    food = foods[weather]

    st.success(food["reason"])

    image = Image.open(food["image"])
    st.image(image, width=500)

    st.subheader(food["name"])

    st.markdown(f"### 🔥 칼로리")
    st.write(food["calorie"])

    st.markdown("### 🥗 영양성분")

    col1, col2, col3 = st.columns(3)

    col1.metric("탄수화물", food["nutrition"]["탄수화물"])
    col2.metric("단백질", food["nutrition"]["단백질"])
    col3.metric("지방", food["nutrition"]["지방"])

    st.progress(0.8)

    st.info("맛있게 드세요! 😊")
