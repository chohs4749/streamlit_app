import streamlit as st

st.set_page_config(page_title="🐧 Penguin Finder", page_icon="🐧", layout="centered")

PENGUINS = {
    "황제펭귄": {
        "서식지":"남극","키":"100~122 cm","몸무게":"22~45 kg",
        "먹이":"크릴, 물고기, 오징어",
        "특징":"현존하는 가장 큰 펭귄"
    },
    "아델리펭귄": {
        "서식지":"남극","키":"46~71 cm","몸무게":"3.5~6 kg",
        "먹이":"크릴","특징":"호기심이 많음"
    },
    "젠투펭귄": {
        "서식지":"남극 주변","키":"75~90 cm","몸무게":"5~8 kg",
        "먹이":"크릴, 물고기","특징":"수영 속도가 매우 빠름"
    },
    "턱끈펭귄": {
        "서식지":"남극","키":"68~76 cm","몸무게":"3~5 kg",
        "먹이":"크릴","특징":"턱 아래 검은 줄"
    },
    "리틀블루펭귄": {
        "서식지":"호주, 뉴질랜드","키":"30~35 cm","몸무게":"1~1.5 kg",
        "먹이":"작은 물고기","특징":"가장 작은 펭귄"
    }
}

st.markdown("""
<style>
.stApp{background:linear-gradient(#dff6ff,#f7fcff);}
.box{background:white;padding:20px;border-radius:18px;border:2px solid #79c7ff;}
</style>
""", unsafe_allow_html=True)

st.title("🐧 Penguin Finder")
st.write("검색창에 펭귄 이름을 입력해 보세요.")

query = st.text_input("🔍 펭귄 이름")

if query:
    found = False
    for name, info in PENGUINS.items():
        if query.lower() in name.lower():
            found = True
            st.markdown(f"<div class='box'><h2>🐧 {name}</h2></div>", unsafe_allow_html=True)
            st.write(f"**📍 서식지:** {info['서식지']}")
            st.write(f"**📏 키:** {info['키']}")
            st.write(f"**⚖️ 몸무게:** {info['몸무게']}")
            st.write(f"**🐟 먹이:** {info['먹이']}")
            st.write(f"**⭐ 특징:** {info['특징']}")
            st.success("검색 완료!")
            break
    if not found:
        st.error("해당 펭귄을 찾을 수 없습니다.")
else:
    st.info("예: 황제펭귄, 젠투펭귄")

