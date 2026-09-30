import streamlit as st

st.title("레이저 광학 시뮬레이터")

st.write("볼록렌즈, 오목렌즈, 볼록거울, 오목거울, 평면거울, 프리즘의 광선 경로를 확인할 수 있습니다.")

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="레이저 광학 시뮬레이터")

st.title("🔴 레이저 광학 시뮬레이터")

object_type = st.selectbox(
    "광학 기구를 선택하세요",
    ["평면거울", "평면판", "프리즘",
     "볼록렌즈", "오목렌즈",
     "볼록거울", "오목거울"]
)

angle = st.slider(
    "레이저 입사각",
    -60.0, 60.0, 0.0, 1.0
)

st.write(f"현재 입사각: **{angle}°**")

fig, ax = plt.subplots(figsize=(10, 6))

# 광축
ax.axhline(0, color="black", linewidth=1)

# 레이저 시작점
x0 = -8
y0 = 0

theta = np.radians(angle)

# 평면거울 위치
mirror_x = 2

# 거울 표시
if object_type == "평면거울":

    ax.plot(
        [mirror_x, mirror_x],
        [-4, 4],
        color="black",
        linewidth=5
    )

    # 거울에 도달하는 위치
    dx = np.cos(theta)
    dy = np.sin(theta)

    distance = (mirror_x - x0) / dx
    hit_y = y0 + distance * dy

    # 입사 광선
    ax.plot(
        [x0, mirror_x],
        [y0, hit_y],
        color="red",
        linewidth=3
    )

    # 반사 광선
    reflected_length = 6

    ax.plot(
        [
            mirror_x,
            mirror_x - reflected_length * dx
        ],
        [
            hit_y,
            hit_y + reflected_length * dy
        ],
        color="red",
        linewidth=3
    )

ax.set_xlim(-10, 10)
ax.set_ylim(-6, 6)

ax.set_xlabel("x")
ax.set_ylabel("y")

ax.grid(True)

st.pyplot(fig)
n1 = 1.0
n2 = 1.5

theta1 = np.radians(angle)

theta2 = np.arcsin(
    n1 * np.sin(theta1) / n2
)
triangle_x = [-2, 0, 2, -2]
triangle_y = [-2, 2, -2, -2]

ax.plot(triangle_x, triangle_y)
