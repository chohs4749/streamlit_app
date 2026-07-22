# app.py
# YouTube Comment Analyzer (starter)

import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="유튜브 댓글 분석기", layout="wide")
st.title("📺 유튜브 댓글 분석기")

API_KEY = st.secrets["YOUTUBE_API_KEY"]
youtube = build("youtube","v3",developerKey=API_KEY)

def extract_video_id(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    if "youtube.com" in url:
        return parse_qs(urlparse(url).query).get("v",[None])[0]
    return None

st.info("이 파일은 시작용 app.py입니다. 전체 프로젝트는 길이 제한 때문에 여러 파일로 제공해야 합니다.")

url = st.text_input("유튜브 URL")

if st.button("분석"):
    vid = extract_video_id(url)
    if not vid:
        st.error("올바른 URL이 아닙니다.")
    else:
        st.success(f"Video ID: {vid}")
