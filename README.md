import streamlit as st
from penguins import PENGUINS
st.set_page_config(page_title="Penguin Finder",page_icon="🐧")
st.markdown("<h1 style='text-align:center'>🐧 Penguin Finder</h1>",unsafe_allow_html=True)
q=st.text_input("펭귄 이름 검색","")
if q:
    found=None
    for k,v in PENGUINS.items():
        if q.lower() in k.lower():
            found=(k,v);break
    if found:
        k,v=found
        st.success(f"{k}")
        for kk,vv in v.items():
            st.write(f"**{kk}**: {vv}")
    else:
        st.error("검색 결과가 없습니다.")
