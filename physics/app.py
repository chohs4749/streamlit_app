import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# 페이지 설정 (전체 화면 활용)
st.set_page_config(page_title="Optical Simulation", layout="wide")

# 사이드바 설정 (오로지 도구 및 모드 선택용)
st.sidebar.markdown("### TOOL")
element_type = st.sidebar.selectbox(
    "",
    [
        "CONVEX LENS",
        "CONCAVE LENS",
        "FLAT MIRROR",
        "CONVEX MIRROR",
        "CONCAVE MIRROR",
        "PRISM",
    ],
    label_visibility="collapsed",
)

refraction_model = "REAL (2-SURFACE)"
if "LENS" in element_type or element_type == "PRISM":
  st.sidebar.markdown("### MODEL")
  refraction_model = st.sidebar.radio(
      "",
      ["TEXTBOOK (1-CENTER)", "REAL (2-SURFACE)"],
      label_visibility="collapsed",
  )

st.sidebar.markdown("---")

# --- 마우스 드래그로 조작하는 슬라이더 (위치 및 각도 실시간 변경) ---
laser_x = st.slider("LASER POSITION X", -8.0, -3.0, -6.0, 0.1)
laser_y = st.slider("LASER POSITION Y", -3.0, 3.0, 1.0, 0.1)
laser_angle = st.slider("LASER ANGLE", -45.0, 45.0, 0.0, 1.0)

element_x = st.slider("ELEMENT POSITION X", -2.0, 2.0, 0.0, 0.1)
element_size = st.slider("ELEMENT SIZE", 0.6, 2.0, 1.0, 0.1)

# --- 격자, 축, 테두리가 전혀 없는 순수 광학 시뮬레이션 화면 생성 ---
fig, ax = plt.subplots(figsize=(11, 5))
ax.set_xlim(-10, 10)
ax.set_ylim(-5, 5)
ax.set_aspect("equal")

# 직사각형 좌표계 및 테두리, 수치, 글자 완전 제거
ax.axis("off")

# 레이저 방향 벡터 계산
rad = np.radians(laser_angle)
dx = np.cos(rad)
dy = np.sin(rad)
lx, ly = laser_x, laser_y

ex = element_x

# --- 광학 도구 및 광선 시각화 (오직 검정색 실선과 점선만 사용) ---
def render_optics():
  # 1. 렌즈 렌더링
  if "LENS" in element_type:
    h = 2.5 * element_size
    yy = np.linspace(-h, h, 100)

    if "CONVEX" in element_type:
      xx_left = ex - 0.3 * element_size * (1 - (yy / h) ** 2)
      xx_right = ex + 0.3 * element_size * (1 - (yy / h) ** 2)
      ax.plot(xx_left, yy, color="black", linewidth=2, linestyle="-")
      ax.plot(xx_right, yy, color="black", linewidth=2, linestyle="-")
    else:
      xx_left = ex - 0.3 * element_size * (0.3 + 0.7 * (yy / h) ** 2)
      xx_right = ex + 0.3 * element_size * (0.3 + 0.7 * (yy / h) ** 2)
      ax.plot(xx_left, yy, color="black", linewidth=2, linestyle="-")
      ax.plot(xx_right, yy, color="black", linewidth=2, linestyle="-")

    hit_y = ly + (dy / dx) * (ex - lx) if dx != 0 else ly
    
    # 입사 레이저 (검정색 실선)
    ax.plot([lx, ex], [ly, hit_y], color="black", linewidth=2.5, linestyle="-")

    if refraction_model == "TEXTBOOK (1-CENTER)":
      # 교과서 버전: 중심 1회 굴절 (검정색 점선 중심선)
      ax.plot([ex, ex], [-h - 0.5, h + 0.5], color="black", linewidth=1.5, linestyle=":")

      if "CONVEX" in element_type:
        exit_slope = -hit_y / (3.0 / element_size)
      else:
        exit_slope = hit_y / (3.0 / element_size)

      end_x = 10.0
      end_y = hit_y + exit_slope * (end_x - ex)
      
      # 굴절 레이저 (검정색 실선)
      ax.plot([ex, end_x], [hit_y, end_y], color="black", linewidth=2.5, linestyle="-")
      # 연장선 (검정색 점선)
      ax.plot([ex, ex - 4.0], [hit_y, hit_y - exit_slope * 4.0], color="black", linewidth=1.5, linestyle=":")

    else:
      # 실제 버전: 표면 2회 굴절
      front_x = ex - 0.2 * element_size
      back_x = ex + 0.2 * element_size
      inside_y = hit_y * 0.85

      # 내부 경로 (검정색 점선)
      ax.plot([front_x, back_x], [hit_y, inside_y], color="black", linewidth=1.5, linestyle=":")
      
      exit_slope = (-inside_y / (2.5 / element_size) if "CONVEX" in element_type else inside_y / (2.5 / element_size))
      end_x = 10.0
      end_y = inside_y + exit_slope * (end_x - back_x)
      
      # 최종 출사 레이저 (검정색 실선)
      ax.plot([back_x, end_x], [inside_y, end_y], color="black", linewidth=2.5, linestyle="-")

  # 2. 거울 렌더링
  elif "MIRROR" in element_type:
    h = 2.5 * element_size
    yy = np.linspace(-h, h, 100)

    if "FLAT" in element_type:
      xx = np.full_like(yy, ex)
      ax.plot(xx, yy, color="black", linewidth=3, linestyle="-")
    elif "CONVEX" in element_type:
      xx = ex - 0.4 * element_size * (yy / h) ** 2
      ax.plot(xx, yy, color="black", linewidth=3, linestyle="-")
    else:
      xx = ex + 0.4 * element_size * (yy / h) ** 2
      ax.plot(xx, yy, color="black", linewidth=3, linestyle="-")

    hit_y = ly + (dy / dx) * (ex - lx) if dx != 0 else ly
    
    # 입사 레이저 (검정색 실선)
    ax.plot([lx, ex], [ly, hit_y], color="black", linewidth=2.5, linestyle="-")

    refl_dx = -dx
    refl_dy = dy
    if "CONVEX" in element_type:
      refl_dy += 0.15 * hit_y
    elif "CONVEX" not in element_type and "FLAT" not in element_type:
      refl_dy -= 0.15 * hit_y

    end_x = -10.0
    end_y = hit_y + (refl_dy / (refl_dx if refl_dx != 0 else 0.001)) * (end_x - ex)
    
    # 반사 레이저 (검정색 실선)
    ax.plot([ex, end_x], [hit_y, end_y], color="black", linewidth=2.5, linestyle="-")
    # 반사 연장선 (검정색 점선)
    ax.plot([ex, ex + 6.0], [hit_y, hit_y - (end_y - hit_y) * 6 / (end_x - ex)], color="black", linewidth=1.5, linestyle=":")

  # 3. 프리즘 렌더링
  elif element_type == "PRISM":
    sz = 1.5 * element_size
    tri_x = [ex - sz, ex, ex + sz, ex - sz]
    tri_y = [-sz, sz, -sz, -sz]
    ax.plot(tri_x, tri_y, color="black", linewidth=2, linestyle="-")

    hit_y = 0.0
    
    # 입사 레이저 (검정색 실선)
    ax.plot([lx, ex - sz * 0.5], [ly, hit_y], color="black", linewidth=2.5, linestyle="-")

    if refraction_model == "TEXTBOOK (1-CENTER)":
      # 교과서 중심선 (검정색 점선)
      ax.plot([ex, ex], [-sz, sz], color="black", linewidth=1.5, linestyle=":")
      # 굴절 레이저 (검정색 실선)
      ax.plot([ex, 10.0], [hit_y, hit_y - 3.0], color="black", linewidth=2.5, linestyle="-")
    else:
      # 내부 경로 (검정색 점선)
      ax.plot([ex - sz * 0.5, ex + sz * 0.3], [hit_y, hit_y - 0.5], color="black", linewidth=1.5, linestyle=":")
      # 최종 출사 레이저 (검정색 실선)
      ax.plot([ex + sz * 0.3, 10.0], [hit_y - 0.5, hit_y - 3.5], color="black", linewidth=2.5, linestyle="-")

# 렌더링 실행
render_optics()

# 레이저 광원 손잡이 표시 (검정색 원)
ax.plot(laser_x, laser_y, marker="o", markersize=12, color="black", markeredgecolor="black")

# 여백 제거 및 순수 도면 출력
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
st.pyplot(fig, use_container_width=True)
