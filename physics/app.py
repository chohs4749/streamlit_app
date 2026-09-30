import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# --- 1. Matplotlib 한글 깨짐 방지 설정 ---
plt.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우 기본 돋움/맑은 고딕
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 페이지 설정
st.set_page_config(
    page_title="물리 광학 발표용 시뮬레이션", page_icon="🔦", layout="wide"
)

st.title("🔦 레이저 광학 실시간 시뮬레이션")

# --- 사이드바: 조작 패널 (드래그 슬라이더 활용) ---
st.sidebar.header("🕹️ 조작 제어판")

# 1. 광학 도구 선택
element_type = st.sidebar.selectbox(
    "광학 도구 선택",
    [
        "볼록렌즈",
        "오목렌즈",
        "평면거울",
        "볼록거울",
        "오목거울",
        "프리즘",
    ],
)

# 굴절 모델 선택 (렌즈와 프리즘일 때만 활성화)
refraction_model = "실제 버전 (표면 2회 굴절)"
if "렌즈" in element_type or element_type == "프리즘":
  refraction_model = st.sidebar.radio(
      "굴절 방식 선택",
      ["교과서 버전 (중간 1회 굴절)", "실제 버전 (표면 2회 굴절)"],
  )

st.sidebar.markdown("---")
st.sidebar.subheader("🖐️ 레이저 손잡이 조작")
laser_x = st.sidebar.slider("손잡이 위치 (앞뒤)", -8.0, -3.0, -6.0, 0.1)
laser_y = st.sidebar.slider("손잡이 높이 (위아래)", -3.0, 3.0, 1.0, 0.1)
laser_angle = st.sidebar.slider("레이저 발사 각도", -45.0, 45.0, 0.0, 1.0)

st.sidebar.markdown("---")
st.sidebar.subheader("📐 광학 도구 위치 및 크기")
element_x = st.sidebar.slider("도구 위치 (앞뒤)", -2.0, 2.0, 0.0, 0.1)
element_size = st.sidebar.slider("도구 두께 및 크기", 0.6, 2.0, 1.0, 0.1)

# --- 메인 플롯 생성 ---
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.set_xlim(-10, 10)
ax.set_ylim(-5, 5)
ax.axhline(0, color="gray", linestyle="--", alpha=0.4)
ax.set_aspect("equal")
ax.grid(True, alpha=0.2)

# 축 및 레이블 텍스트 정리 (글자 깨짐 방지 적용)
ax.set_xlabel("광축 거리", fontsize=11)
ax.set_ylabel("높이", fontsize=11)

# 레이저 방향 벡터 계산
rad = np.radians(laser_angle)
dx = np.cos(rad)
dy = np.sin(rad)
lx, ly = laser_x, laser_y


# --- 광학 도구 및 광선 추적 시각화 함수 ---
def draw_simulation():
  ex = element_x

  # --- [1] 렌즈 그리기 및 광선 추적 ---
  if "렌즈" in element_type:
    h = 2.5 * element_size
    yy = np.linspace(-h, h, 100)

    if "볼록" in element_type:
      # 실제 볼록렌즈 모양 (가운데가 두껍고 끝이 뾰족)
      xx_left = ex - 0.3 * element_size * (1 - (yy / h) ** 2)
      xx_right = ex + 0.3 * element_size * (1 - (yy / h) ** 2)
      ax.fill_betweenx(
          yy, xx_left, xx_right, color="dodgerblue", alpha=0.3, label="볼록렌즈"
      )
      ax.plot(xx_left, yy, color="blue", linewidth=1.5)
      ax.plot(xx_right, yy, color="blue", linewidth=1.5)
    else:
      # 실제 오목렌즈 모양 (가운데가 얇고 끝이 두꺼움)
      xx_left = ex - 0.3 * element_size * (0.3 + 0.7 * (yy / h) ** 2)
      xx_right = ex + 0.3 * element_size * (0.3 + 0.7 * (yy / h) ** 2)
      ax.fill_betweenx(
          yy, xx_left, xx_right, color="mediumpurple", alpha=0.3, label="오목렌즈"
      )
      ax.plot(xx_left, yy, color="purple", linewidth=1.5)
      ax.plot(xx_right, yy, color="purple", linewidth=1.5)

    # 입사 광선 계산
    hit_y = ly + (dy / dx) * (ex - lx) if dx != 0 else ly
    ax.plot([lx, ex], [ly, hit_y], color="red", linewidth=2.5, label="입사 레이저")

    if refraction_model == "교과서 버전 (중간 1회 굴절)":
      # 교과서식: 렌즈 중심선에서 한번에 꺾임
      ax.plot(
          [ex, ex],
          [-h - 0.5, h + 0.5],
          color="gray",
          linestyle=":",
          linewidth=1.5,
          label="교과서 중심 굴절선",
      )

      if "볼록" in element_type:
        exit_slope = -hit_y / (3.0 / element_size)
      else:
        exit_slope = hit_y / (3.0 / element_size)

      end_x = 10.0
      end_y = hit_y + exit_slope * (end_x - ex)
      ax.plot(
          [ex, end_x],
          [hit_y, end_y],
          color="darkorange",
          linewidth=2.5,
          label="굴절 레이저",
      )
      # 연장선 (점선)
      ax.plot(
          [ex, ex - 4.0],
          [hit_y, hit_y - exit_slope * 4.0],
          color="darkorange",
          linestyle=":",
          alpha=0.6,
          label="연장선",
      )

    else:
      # 실제 버전: 표면 2회 굴절
      front_x = ex - 0.2 * element_size
      back_x = ex + 0.2 * element_size
      inside_y = hit_y * 0.85

      ax.plot(
          [front_x, back_x],
          [hit_y, inside_y],
          color="magenta",
          linestyle="--",
          linewidth=1.5,
          label="렌즈 내부 경로",
      )
      exit_slope = (
          -inside_y / (2.5 / element_size)
          if "볼록" in element_type
          else inside_y / (2.5 / element_size)
      )
      end_x = 10.0
      end_y = inside_y + exit_slope * (end_x - back_x)
      ax.plot(
          [back_x, end_x],
          [inside_y, end_y],
          color="darkorange",
          linewidth=2.5,
          label="최종 출사 레이저",
      )

  # --- [2] 거울 그리기 및 반사 추적 ---
  elif "거울" in element_type:
    h = 2.5 * element_size
    yy = np.linspace(-h, h, 100)

    if "평면" in element_type:
      xx = np.full_like(yy, ex)
      ax.plot(xx, yy, color="black", linewidth=4, label="평면거울")
    elif "볼록" in element_type:
      xx = ex - 0.4 * element_size * (yy / h) ** 2
      ax.plot(xx, yy, color="forestgreen", linewidth=3.5, label="볼록거울")
    else:  # 오목거울
      xx = ex + 0.4 * element_size * (yy / h) ** 2
      ax.plot(xx, yy, color="firebrick", linewidth=3.5, label="오목거울")

    hit_y = ly + (dy / dx) * (ex - lx) if dx != 0 else ly
    ax.plot([lx, ex], [ly, hit_y], color="red", linewidth=2.5, label="입사 레이저")

    # 반사 계산
    refl_dx = -dx
    refl_dy = dy
    if "볼록" in element_type:
      refl_dy += 0.15 * hit_y
    elif "오목" in element_type:
      refl_dy -= 0.15 * hit_y

    end_x = -10.0
    end_y = hit_y + (refl_dy / (refl_dx if refl_dx != 0 else 0.001)) * (
        end_x - ex
    )
    ax.plot(
        [ex, end_x],
        [hit_y, end_y],
        color="darkorange",
        linewidth=2.5,
        label="반사 레이저",
    )
    # 반사 연장선 (점선)
    ax.plot(
        [ex, ex + 6.0],
        [hit_y, hit_y - (end_y - hit_y) * 6 / (end_x - ex)],
        color="darkorange",
        linestyle=":",
        alpha=0.6,
        label="반사 연장선",
    )

  # --- [3] 프리즘 그리기 및 굴절 추적 ---
  elif element_type == "프리즘":
    sz = 1.5 * element_size
    tri_x = [ex - sz, ex, ex + sz, ex - sz]
    tri_y = [-sz, sz, -sz, -sz]
    ax.plot(
        tri_x,
        tri_y,
        color="teal",
        linewidth=2,
        label="삼각 프리즘",
    )
    ax.fill(tri_x, tri_y, color="teal", alpha=0.15)

    hit_y = 0.0
    ax.plot([lx, ex - sz * 0.5], [ly, hit_y], color="red", linewidth=2.5, label="입사 레이저")

    if refraction_model == "교과서 버전 (중간 1회 굴절)":
      ax.plot(
          [ex, ex],
          [-sz, sz],
          color="gray",
          linestyle=":",
          linewidth=1.5,
          label="교과서 중심 굴절선",
      )
      ax.plot(
          [ex, 10.0],
          [hit_y, hit_y - 3.0],
          color="darkorange",
          linewidth=2.5,
          label="굴절/분산 레이저",
      )
    else:
      ax.plot(
          [ex - sz * 0.5, ex + sz * 0.3],
          [hit_y, hit_y - 0.5],
          color="magenta",
          linestyle="--",
          linewidth=1.5,
          label="프리즘 내부 경로",
      )
      ax.plot(
          [ex + sz * 0.3, 10.0],
          [hit_y - 0.5, hit_y - 3.5],
          color="darkorange",
          linewidth=2.5,
          label="최종 출사 레이저",
      )


# 시뮬레이션 드로잉 실행
draw_simulation()

# 레이저가 나오는 손잡이(광원) 표시
ax.plot(
    laser_x,
    laser_y,
    marker="o",
    markersize=14,
    color="crimson",
    markeredgecolor="black",
    label="레이저 손잡이",
)
ax.text(
    laser_x,
    laser_y + 0.35,
    "레이저 손잡이",
    color="crimson",
    fontsize=10,
    fontweight="bold",
    ha="center",
)

# 그래프 레이아웃 설정
ax.set_title(
    f"선택 도구: [{element_type}]", fontsize=13, fontweight="bold", pad=15
)
ax.legend(loc="upper right", fontsize=9)

# 스트림릿 웹 화면에 출력
st.pyplot(fig)
