import streamlit as st

st.set_page_config(page_title="🐧 Penguin Finder", page_icon="🐧", layout="centered")

PENGUINS = {
    "황제펭귄": {
        "서식지": "남극",
        "키": "100~122 cm",
        "몸무게": "22~45 kg",
        "먹이": "크릴, 물고기, 오징어",
        "특징": "현존하는 가장 큰 펭귄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/0/07/Emperor_Penguin_Manchot_empereur.jpg"
    },
    "임금펭귄": {
        "서식지": "아남극 도서 지역",
        "키": "85~95 cm",
        "몸무게": "11~16 kg",
        "먹이": "작은 물고기, 오징어",
        "특징": "황제펭귄 다음으로 큰 펭귄, 목에 선명한 주황색 띠",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/2/22/King_penguin_st_andrews_bay_sea_lion_2.jpg"
    },
    "아델리펭귄": {
        "서식지": "남극 대륙 연안",
        "키": "46~71 cm",
        "몸무게": "3.5~6 kg",
        "먹이": "크릴, 작은 물고기",
        "특징": "눈 둘레의 하얀 테두리가 특징이며 호기심이 매우 많음",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Adelie_Penguin_in_Antarctica.jpg"
    },
    "젠투펭귄": {
        "서식지": "남극 및 아남극 섬",
        "키": "75~90 cm",
        "몸무게": "5~8.5 kg",
        "먹이": "크릴, 물고기",
        "특징": "머리 위에 흰색 띠가 있으며 수영 속도가 가장 빠른 펭귄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/0/00/Brown_Bluff-2013-Gentoo_penguin_%28Pygoscelis_papua%29.jpg"
    },
    "턱끈펭귄": {
        "서식지": "남극 및 아남극 섬",
        "키": "68~76 cm",
        "몸무게": "3~5 kg",
        "먹이": "크릴, 작은 물고기",
        "특징": "턱 아래를 지나는 가느다란 검은 줄무늬가 특징",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/0/08/South_Shetland-2016-Deception_Island%E2%80%93Chinstrap_penguin_%28Pygoscelis_antarcticus%29_04.jpg"
    },
    "리틀블루펭귄": {
        "서식지": "호주, 뉴질랜드",
        "키": "30~35 cm",
        "몸무게": "1~1.5 kg",
        "먹이": "작은 물고기, 오징어",
        "특징": "세계에서 가장 작은 펭귄, 깃털이 푸른빛을 띰",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Little_penguin_wildlife_park.jpg"
    },
    "마카로니펭귄": {
        "서식지": "남극 주변 섬",
        "키": "70 cm",
        "몸무게": "5.5 kg",
        "먹이": "크릴, 오징어",
        "특징": "머리에 화려한 노란색 깃털 벼슬이 있음",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/8/87/Eudyptes_chrysolophus_1.jpg"
    },
    "남방바위뛰기펭귄": {
        "서식지": "남아메리카 남부, 남극 주변 섬",
        "키": "45~58 cm",
        "몸무게": "2~3.4 kg",
        "먹이": "크릴, 오징어",
        "특징": "가파른 바위 절벽을 깡충깡충 뛰어다님",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Southern_Rockhopper_Penguin.jpg"
    },
    "갈라파고스펭귄": {
        "서식지": "갈라파고스 제도",
        "키": "49 cm",
        "몸무게": "2.5 kg",
        "먹이": "작은 물고기",
        "특징": "적도에 사는 유일한 펭귄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Galapagos_Penguin_Bartolome.jpg"
    },
    "아프리카펭귄": {
        "서식지": "아프리카 남부 해안",
        "키": "60~70 cm",
        "몸무게": "2.2~3.5 kg",
        "먹이": "정어리, 멸치",
        "특징": "가슴에 독특한 C자형 검은 띠가 있으며 '자갈펭귄'이라고도 불림",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/6/63/African_penguin_side_view.jpg"
    },
    "마젤란펭귄": {
        "서식지": "아르헨티나, 칠레, 포클랜드 제도",
        "키": "61~76 cm",
        "몸무게": "2.7~6.5 kg",
        "먹이": "오징어, 정어리",
        "특징": "목에 두 개의 검은 테두리가 있음",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/d/d2/Magellanic_penguin%2C_Otway_Sound%2C_Chile.jpg"
    },
    "훔볼트펭귄": {
        "서식지": "페루, 칠레 연안",
        "키": "56~70 cm",
        "몸무게": "3.6~5.9 kg",
        "먹이": "멸치, 정어리",
        "특징": "부리 주변의 분홍색 맨살이 특징",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/4/41/Humboldt-pinguin.jpg"
    },
    "노란눈펭귄": {
        "서식지": "뉴질랜드 남섬 및 수브안타크틱 섬",
        "키": "62~79 cm",
        "몸무게": "3~8 kg",
        "먹이": "물고기, 오징어",
        "특징": "선명한 노란색 눈과 머리의 노란 띠가 특징인 희귀 펭귄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Yellow-eyed_penguin_Katiki_Point.jpg"
    }
}

# CSS 구문 열고 닫기를 정돈하였습니다.
st.markdown("""
<style>
.stApp { background: linear-gradient(#dff6ff, #f7fcff); }
.box { background: white; padding: 20px; border-radius: 18px; border: 2px solid #79c7ff; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

st.title("🐧 Penguin Finder")
st.write("검색창에 펭귄 이름을 입력해 보세요. (총 13종 수록)")

query = st.text_input("🔍 펭귄 이름")

if query:
    matches = [name for name in PENGUINS.keys() if query.strip().lower() in name.lower()]
    
    if matches:
        for name in matches:
            info = PENGUINS[name]
            st.markdown(f"<div class='box'><h2>🐧 {name}</h2></div>", unsafe_allow_html=True)
            
            # 펭귄 사진 표시
            if "이미지" in info and info["이미지"]:
                st.image(info["이미지"], caption=f"{name}", use_column_width=True)
                
            st.write(f"**📍 서식지:** {info['서식지']}")
            st.write(f"**📏 키:** {info['키']}")
            st.write(f"**⚖️ 몸무게:** {info['몸무게']}")
            st.write(f"**🐟 먹이:** {info['먹이']}")
            st.write(f"**⭐ 특징:** {info['특징']}")
            st.divider()
        st.success(f"총 {len(matches)}종의 펭귄 정보를 찾았습니다!")
    else:
        st.error("해당 펭귄을 찾을 수 없습니다.")
else:
    st.info("예: 황제펭귄, 젠투펭귄, 아프리카펭귄, 갈라파고스펭귄")
