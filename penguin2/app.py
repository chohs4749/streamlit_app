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
