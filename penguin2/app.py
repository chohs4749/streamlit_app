import streamlit as st

st.set_page_config(page_title="🐧 Penguin Finder", page_icon="🐧", layout="centered")

# 전 세계 18종 펭귄 정보 및 검증된 펭귄 고유 이미지 URL (위키미디어 공헌 출처)
PENGUINS = {
    "황제펭귄": {
        "영명": "Emperor Penguin",
        "서식지": "남극 대륙",
        "키": "100~122 cm",
        "몸무게": "22~45 kg",
        "먹이": "크릴, 물고기, 오징어",
        "특징": "현존하는 펭귄 중 가장 큼. 혹독한 추위 속에서 수컷이 알을 낳아 품음",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/0/07/Emperor_Penguin_Manchot_empereur.jpg"
    },
    "임금펭귄": {
        "영명": "King Penguin",
        "서식지": "아남극 제도 (포클랜드, 사우스조지아 등)",
        "키": "85~95 cm",
        "몸무게": "11~16 kg",
        "먹이": "작은 물고기, 오징어",
        "특징": "황제펭귄 다음으로 큼. 목과 부리 주위의 선명한 주황색 깃털이 특징",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/2/22/King_penguin_st_andrews_bay_sea_lion_2.jpg"
    },
    "아델리펭귄": {
        "영명": "Adélie Penguin",
        "서식지": "남극 대륙 연안",
        "키": "46~71 cm",
        "몸무게": "3.5~6 kg",
        "먹이": "크릴, 작은 물고기",
        "특징": "눈 둘레의 하얀 테두리가 매력적이며 호기심이 많고 호전적임",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Adelie_Penguin_in_Antarctica.jpg"
    },
    "젠투펭귄": {
        "영명": "Gentoo Penguin",
        "서식지": "남극반도 및 아남극 섬",
        "키": "75~90 cm",
        "몸무게": "5~8.5 kg",
        "먹이": "크릴, 물고기",
        "특징": "머리 위의 흰 양말 모양 띠와 주황색 부리가 특징이며 수영 속도가 가장 빠름",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/0/00/Brown_Bluff-2013-Gentoo_penguin_%28Pygoscelis_papua%29.jpg"
    },
    "턱끈펭귄": {
        "영명": "Chinstrap Penguin",
        "서식지": "남극 및 아남극 섬",
        "키": "68~76 cm",
        "몸무게": "3~5 kg",
        "먹이": "크릴, 작은 물고기",
        "특징": "턱 아래를 가로지르는 가느다란 검은 줄무늬(턱끈)가 헬멧을 쓴 듯함",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/0/08/South_Shetland-2016-Deception_Island%E2%80%93Chinstrap_penguin_%28Pygoscelis_antarcticus%29_04.jpg"
    },
    "리틀블루펭귄": {
        "영명": "Little Blue Penguin",
        "서식지": "호주 남부, 뉴질랜드",
        "키": "30~35 cm",
        "몸무게": "1~1.5 kg",
        "먹이": "작은 물고기, 오징어",
        "특징": "세계에서 가장 작은 펭귄으로, 깃털이 푸른빛을 띰 ('요정펭귄'으로도 불림)",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Little_penguin_wildlife_park.jpg"
    },
    "마카로니펭귄": {
        "영명": "Macaroni Penguin",
        "서식지": "아남극 및 남극 주변 섬",
        "키": "70 cm",
        "몸무게": "5.5 kg",
        "먹이": "크릴, 오징어",
        "특징": "머리에 화려하고 깃털 모양의 주황 노란색 벼슬이 솟아있음",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/8/87/Eudyptes_chrysolophus_1.jpg"
    },
    "남방바위뛰기펭귄": {
        "영명": "Southern Rockhopper Penguin",
        "서식지": "남아메리카 남부, 아남극 섬",
        "키": "45~58 cm",
        "몸무게": "2~3.4 kg",
        "먹이": "크릴, 오징어",
        "특징": "붉은 눈과 노란 깃털 벼슬을 가졌으며 바위 절벽을 깡충깡충 잘 뛰어다님",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Southern_Rockhopper_Penguin.jpg"
    },
    "북방바위뛰기펭귄": {
        "영명": "Northern Rockhopper Penguin",
        "서식지": "남대서양 트리스탄다쿠냐 섬 등",
        "키": "55 cm",
        "몸무게": "3 kg",
        "먹이": "갑각류, 오징어",
        "특징": "남방바위뛰기펭귄보다 벼슬이 길고 풍성하며 멸종위기종에 해당함",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Northern_Rockhopper_Penguin.jpg"
    },
    "갈라파고스펭귄": {
        "영명": "Galapagos Penguin",
        "서식지": "에콰도르 갈라파고스 제도",
        "키": "49 cm",
        "몸무게": "2.5 kg",
        "먹이": "작은 물고기(숭어, 정어리)",
        "특징": "적도 부근의 따뜻한 지역에 사는 유일한 펭귄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Galapagos_Penguin_Bartolome.jpg"
    },
    "아프리카펭귄": {
        "영명": "African Penguin (Jackass Penguin)",
        "서식지": "아프리카 남부 해안 (나미비아, 남아공)",
        "키": "60~70 cm",
        "몸무게": "2.2~3.5 kg",
        "먹이": "정어리, 멸치",
        "특징": "가슴에 C자형 검은 띠가 있고 당나귀 울음소리와 비슷한 소리를 냄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/6/63/African_penguin_side_view.jpg"
    },
    "마젤란펭귄": {
        "영명": "Magellanic Penguin",
        "서식지": "남아메리카(아르헨티나, 칠레 연안)",
        "키": "61~76 cm",
        "몸무게": "2.7~6.5 kg",
        "먹이": "오징어, 정어리",
        "특징": "목에 두 개의 검은 테두리가 있으며 굴을 파서 번식함",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/d/d2/Magellanic_penguin%2C_Otway_Sound%2C_Chile.jpg"
    },
    "훔볼트펭귄": {
        "영명": "Humboldt Penguin",
        "서식지": "남아메리카 태평양 연안(페루, 칠레)",
        "키": "56~70 cm",
        "몸무게": "3.6~5.9 kg",
        "먹이": "멸치, 전갱이",
        "특징": "부리 주변에 핑크색 육질이 노출되어 체온 조절을 도움",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/4/41/Humboldt-pinguin.jpg"
    },
    "노란눈펭귄": {
        "영명": "Yellow-eyed Penguin",
        "서식지": "뉴질랜드 남섬 및 서브안타크틱 섬",
        "키": "62~79 cm",
        "몸무게": "3~8 kg",
        "먹이": "물고기, 오징어",
        "특징": "선명한 노란 눈과 머리 주변의 노란 띠가 특징인 세계적 희귀 펭귄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Yellow-eyed_penguin_Katiki_Point.jpg"
    },
    "스네어스펭귄": {
        "영명": "Snares Penguin",
        "서식지": "뉴질랜드 스네어스 제도",
        "키": "50~70 cm",
        "몸무게": "2.5~4 kg",
        "먹이": "크릴, 오징어",
        "특징": "부리 자루 주위의 하얀 피부선과 굵은 벼슬 깃털이 특징",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Snares_Penguin.jpg"
    },
    "피오르드랜드펭귄": {
        "영명": "Fiordland Penguin",
        "서식지": "뉴질랜드 남섬 남서부 해안",
        "키": "60 cm",
        "몸무게": "3~4.5 kg",
        "먹이": "갑각류, 작은 물고기",
        "특징": "볼 부분에 3~5개의 하얀 줄무늬가 있는 수줍음 많은 펭귄",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Fiordland_Penguin.jpg"
    },
    "로열펭귄": {
        "영명": "Royal Penguin",
        "서식지": "호주 맥쿼리 섬",
        "키": "65~75 cm",
        "몸무게": "3~8 kg",
        "먹이": "크릴, 작은 물고기",
        "특징": "마카로니펭귄과 매우 비슷하나 얼굴과 턱이 흰색을 띰",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Royal_Penguin_Macquarie_Island.jpg"
    },
    "화이트플리퍼펭귄": {
        "영명": "White-flippered Penguin",
        "서식지": "뉴질랜드 캔터베리 지역",
        "키": "30 cm",
        "몸무게": "1.5 kg",
        "먹이": "작은 물고기",
        "특징": "리틀블루펭귄의 아종 또는 근연종으로 날개 가장자리에 하얀 띠가 있음",
        "이미지": "https://upload.wikimedia.org/wikipedia/commons/8/88/White-flippered_Penguin.jpg"
    }
}

# 커스텀 CSS 스타일링
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
}
.penguin-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 119, 182, 0.1);
    border: 1px solid #bae6fd;
    margin-bottom: 15px;
}
.penguin-title {
    color: #0369a1;
    font-size: 1.8rem;
    font-weight: bold;
}
.penguin-sub {
    color: #0284c7;
    font-size: 1.0rem;
    font-style: italic;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🐧 Penguin Finder")
st.write(f"전 세계 **{len(PENGUINS)}종의 펭귄** 정보를 한눈에 찾아보세요!")

query = st.text_input("🔍 펭귄 이름 검색 (예: 황제펭귄, 아델리, 갈라파고스, 턱끈)")

if query:
    # 한국어 이름 또는 영문 이름에서 검색어 매칭
    matches = [
        name for name, info in PENGUINS.items() 
        if query.strip().lower() in name.lower() or query.strip().lower() in info["영명"].lower()
    ]
    
    if matches:
        for name in matches:
            info = PENGUINS[name]
            
            st.markdown(f"""
            <div class="penguin-card">
                <div class="penguin-title">🐧 {name}</div>
                <div class="penguin-sub">{info['영명']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 정확한 펭귄 사진 출력
            st.image(info["이미지"], caption=f"{name} ({info['영명']})", use_container_width=True)
                
            st.write(f"**📍 서식지:** {info['서식지']}")
            st.write(f"**📏 키:** {info['키']}")
            st.write(f"**⚖️ 몸무게:** {info['몸무게']}")
            st.write(f"**🐟 주요 먹이:** {info['먹이']}")
            st.write(f"**⭐ 주요 특징:** {info['특징']}")
            st.divider()
            
        st.success(f"총 {len(matches)}종의 검색 결과를 찾았습니다.")
    else:
        st.error("검색하신 펭귄을 찾을 수 없습니다.")
else:
    st.info("💡 팁: 전체 펭귄 목록을 보시려면 아래 창을 클릭해보세요.")
    
    with st.expander("📖 전체 18종 펭귄 목록 보기"):
        cols = st.columns(2)
        for idx, (p_name, p_info) in enumerate(PENGUINS.items()):
            with cols[idx % 2]:
                st.write(f"- **{p_name}** ({p_info['영명']})")
