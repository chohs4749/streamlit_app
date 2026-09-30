import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="물리 광학 발표용 시뮬레이션", page_icon="🔦", layout="wide"
)

st.title("🔦 레이저의 굴절 및 반사 시뮬레이션")
st.markdown(
    "학교 물리 발표용 앱입니다. 사이드바에서 레이저와 광학 도구를 조작하며 빛의 경로를 관찰해보세요!"
)

# --- 사이드바: 조작 패널 ---
st.sidebar.header("⚙️ 시뮬레이션 설정")

# 1. 광학 도구 선택
element_type = st.sidebar.selectbox(
    "광학 도구 선택",
    [
        "볼록렌즈 (Convex Lens)",
        "오목렌즈 (Concave Lens)",
        "평면거울 (Flat Mirror)",
        "볼록거울 (Convex Mirror)",
        "오목거울 (Concave Mirror)",
        "프리즘 (Prism)",
    ],
)

# 굴절 모델 선택 (렌즈와 프리즘일 때만 활성화)
refraction_model = "실제 버전 (표면 2회 굴절)"
if "렌즈" in element_type or "프리즘" in element_type:
  refraction_model = st.sidebar.radio(
      "굴절 모델 선택",
      ["교과서 버전 (중간 1회 굴절)", "실제 버전 (표면 2회 굴절)"],
  )

st.sidebar.markdown("---")
st.sidebar.subheader("📍 레이저 위치 및 각도 조절")
laser_x = st.sidebar.slider("레이저 위치 X", -8.0, -2.0, -6.0, 0.1)
laser_y = st.sidebar.slider("레이저 위치 Y", -3.0, 3.0, 1.0, 0.1)
laser_angle = st.sidebar.slider(
    "레이저 각도 (°)", -50.0, 50.0, 0.0, 1.0
)  # 0도가 수평

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 광학 도구 설정")
element_x = st.sidebar.slider("도구 위치 X", -2.0, 2.0, 0.0, 0.1)
element_thickness = st.sidebar.slider("도구 두께 / 크기", 0.5, 2.5, 1.0, 0.1)

# --- 메인 플롯 생성 ---
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(-10, 10)
ax.set_ylim(-5, 5)
ax.axhline(
    0, color="gray", linestyle="--", alpha=0.5, label="광축 (Optical Axis)"
)
ax.set_aspect("equal")
ax.grid(True, alpha=0.3)

# 레이저 방향 벡터 계산
rad = np.radians(laser_angle)
dx = np.cos(rad)
dy = np.sin(rad)

# 레이저 시작점
lx, ly = laser_x, laser_y


# --- 광학 도구 드로잉 및 광선 추적 로직 ---
def draw_optical_element_and_rays():
  # 공통 광선 (입사 광선: 레이저 ~ 도구 표면)
  # 도구의 중심 X 위치 설정
  ex = element_x

  if "렌즈" in element_type:
    # 렌즈 그리기
    half_h = 2.0 * element_thickness
    if "볼록" in element_type:
      # 볼록렌즈 모양 표현
      ax.plot(
          [ex, ex, ex],
          [-half_h, half_h, -half_h],
          color="blue",
          alpha=0.3,
          linewidth=2,
      )
      ax.text(
          ex,
          half_h + 0.3,
          element_type,
          ha="center",
          fontsize=10,
          color="blue",
      )
    else:
      # 오목렌즈 모양 표현
      ax.plot(
          [ex - 0.2, ex + 0.2, ex + 0.2, ex - 0.2, ex - 0.2],
          [-half_h, -half_h + 0.5, half_h - 0.5, half_h, -half_h],
          color="purple",
          alpha=0.3,
          linewidth=2,
      )
      ax.text(
          ex,
          half_h + 0.3,
          element_type,
          ha="center",
          fontsize=10,
          color="purple",
      )

    # 입사 광선 계산 (도구에 닿을 때까지)
    # y = ly + (dy/dx)*(x - lx) 에서 x = ex 일 때의 y 교점 계산
    if dx != 0:
      t = (ex - lx) / dx
      hit_y = ly + dy * t
    else:
      hit_y = ly

    # 입사 광선 실선 표시
    ax.plot([lx, ex], [ly, hit_y], color="red", linewidth=2, label="입사 레이저")

    if refraction_model == "교과서 버전 (중간 1회 굴절)":
      # 교과서 버전: 렌즈 중앙(ex, 0)에서 한번에 꺾이는 것처럼 표현
      ax.plot(
          [ex, ex], [0, hit_y], color="gray", linestyle=":", label="중심 기준선"
      )
      # 굴절 후 방향 계산 (볼록은 모이고, 오목은 퍼짐)
      focal_length = 3.0 / element_thickness
      if "볼록" in element_type:
        # 초점을 향해 꺾임
        target_y = -hit_y * (1.0 / focal_length) + hit_y * 0.5
      else:
        # 퍼져나감 (가상초점 연장선)
        target_y = hit_y + hit_y * 0.4

      # 굴절 광선 및 연장선(점선)
      end_x = 10.0
      end_y = hit_y + (target_y - hit_y) / (end_x - ex) * (end_x - ex)
      # 간단화된 직진/굴절선
      slope_out = (
          -hit_y / 3.0
          if "볼록" in element_type
          else hit_y / 3.0 + (hit_y * 0.2)
      )
      exit_end_y = hit_y + slope_out * (10.0 - ex)

      ax.plot(
          [ex, 10.0],
          [hit_y, exit_end_y],
          color="orange",
          linewidth=2,
          label="굴절 레이저",
      )
      # 연장선 (점선)
      ax.plot(
          [ex, ex - 4.0],
          [hit_y, hit_y - slope_out * 4.0],
          color="orange",
          linestyle=":",
          alpha=0.6,
      )

    else:
      # 실제 버전: 첫 번째 표면 굴절 -> 내부 진행 -> 두 번째 표면 굴절
      front_x = ex - 0.2 * element_thickness
      back_x = ex + 0.2 * element_thickness

      # 1번 굴절 (입사면)
      ax.plot(
          [lx, front_x],
          [ly, hit_y],
          color="red",
          linewidth=2,
          label="입사 레이저",
      )
      # 내부 진행 (실선 또는 투명선)
      inside_exit_y = hit_y * 0.8  # 대략적인 내부 굴절
      ax.plot(
          [front_x, back_x],
          [hit_y, inside_exit_y],
          color="magenta",
          linewidth=1.5,
          linestyle="--",
          label="내부 경로",
      )
      # 2번 굴절 (출사면)
      exit_slope = (
          -inside_exit_y / 2.5
          if "볼록" in element_type
          else inside_exit_y / 2.5
      )
      final_end_y = inside_exit_y + exit_slope * (10.0 - back_x)
      ax.plot(
          [back_x, 10.0],
          [inside_exit_y, final_end_y],
          color="orange",
          linewidth=2,
          label="최종 굴절 레이저",
      )

  elif "거울" in element_type:
    # 거울 그리기
    half_h = 2.0
    if "평면" in element_type:
      ax.plot(
          [ex, ex], [-half_h, half_h], color="black", linewidth=4, label="평면거울"
      )
    elif "볼록" in element_type:
      yy = np.linspace(-half_h, half_h, 100)
      xx = ex - 0.3 * (yy / half_h) ** 2
      ax.plot(xx, yy, color="darkgreen", linewidth=3, label="볼록거울")
    else:  # 오목거울
      yy = np.linspace(-half_h, half_h, 100)
      xx = ex + 0.3 * (yy / half_h) ** 2
      ax.plot(xx, yy, color="darkred", linewidth=3, label="오목거울")

    # 반사 계산
    if dx != 0:
      t = (ex - lx) / dx
      hit_y = ly + dy * t
    else:
      hit_y = ly

    ax.plot([lx, ex], [ly, hit_y], color="red", linewidth=2, label="입사 레이저")

    # 반사각 계산 (법선 반사 법칙 적용)
    refl_dx = -dx
    refl_dy = dy
    if "볼록" in element_type:
      refl_dy += 0.1 * hit_y
    elif "오목" in element_type:
      refl_dy -= 0.1 * hit_y

    end_x = -10.0  
    end_y = hit_y + (refl_dy / (refl_dx if refl_dx != 0 else 0.001)) * (
        end_x - ex
    )
    ax.plot(
        [ex, end_x],
        [hit_y, end_y],
        color="orange",
        linewidth=2,
        label="반사 레이저",
    )
    # 반사 연장선 (점선)
    ax.plot(
        [ex, ex + 5.0],
        [hit_y, hit_y - (end_y - hit_y) * 5 / (end_x - ex)],
        color="orange",
        linestyle=":",
        alpha=0.6,
        label="반사 연장선",
    )

  elif "프리즘" in element_type:
    # 프리즘 (삼각형) 그리기
    p_bottom = ex - 1.0
    p_top = ex + 1.0
    triangle_x = [p_bottom, ex, p_top, p_bottom]
    triangle_y = [-1.5, 1.5, -1.5, -1.5]
    ax.plot(
        triangle_x,
        triangle_y,
        color="teal",
        linewidth=2,
        label="삼각 프리즘",
    )

    hit_y = 0.0  # 프리즘 입사 지점 간소화
    ax.plot(
        [lx, ex - 0.5],
        [ly, hit_y],
        color="red",
        linewidth=2,
        label="입사 레이저",
    )

    if refraction_model == "교과서 버전 (중간 1회 굴절)":
      ax.plot(
          [ex, ex],
          [-1.5, 1.5],
          color="gray",
          linestyle=":",
          label="중심 굴절선",
      )
      ax.plot(
          [ex, 10.0],
          [hit_y, hit_y - 2.5],
          color="orange",
          linewidth=2,
          label="굴절/분산 레이저",
      )
    else:
      # 실제 2회 굴절 (입사 -> 출사)
      ax.plot(
          [ex - 0.5, ex + 0.5],
          [hit_y, hit_y - 0.5],
          color="magenta",
          linestyle="--",
          label="프리즘 내부 경로",
      )
      ax.plot(
          [ex + 0.5, 10.0],
          [hit_y - 0.5, hit_y - 3.0],
          color="orange",
          linewidth=2,
          label="최종 출사 레이저",
      )


# 광선 그리기 실행
draw_optical_element_and_rays()

# 레이저 손잡이(광원 위치) 마커 표시
ax.plot(
    laser_x,
    laser_y,
    marker="o",
    markersize=12,
    color="red",
    label="레이저 광원 (손잡이)",
)

# 그래프 꾸미기
ax.set_title(
    f"현재 선택: {element_type} ({refraction_model})", fontsize=12, fontweight="bold"
)
ax.set_xlabel("X 위치")
ax.set_ylabel("Y 위치")
ax.legend(loc="upper right", fontsize=9)

# 스트림릿에 그래프 출력
st.pyplot(fig)

# --- 발표 팁 안내 ---
st.info(
    "💡 **발표 팁:** 사이드바의 **'레이저 위치 및 각도'** 슬라이더를 좌우로 움직여 보면 손잡이를 드래그하는 것처럼 실시간으로 빛의 경로가 바뀌는 것을 보여줄 수 있습니다!"
)
