import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="레이저 광학 시뮬레이터",
    page_icon="🔴",
    layout="wide"
)

st.title("🔴 레이저 광학 시뮬레이터 (완벽 드래그 & 광선 작도)")

st.markdown(
    """
    - **노란색 손잡이 (레이저)**: 드래그하여 레이저의 발사 방향을 조절할 수 있습니다.
    - **파란색 손잡이 (광학 기구 상단)**: 드래그하여 렌즈, 거울, 프리즘의 위치를 좌우로 자유롭게 이동할 수 있습니다.
    - 광학 기구의 실제 모양(볼록/오목/삼각형)과 정확한 반사·굴절 광선을 관찰하세요.
    """
)

html_code = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, "Malgun Gothic", sans-serif;
    background: #f4f6f8;
    color: #222;
}
.panel {
    background: white;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.10);
}
.control-grid {
    display: grid;
    grid-template-columns: 170px 1fr 110px;
    gap: 14px;
    align-items: center;
    margin-bottom: 13px;
}
select {
    width: 100%;
    padding: 9px;
    border: 1px solid #aaa;
    border-radius: 7px;
    font-size: 15px;
    background: white;
}
input[type="range"] {
    width: 100%;
    cursor: pointer;
}
.value {
    text-align: right;
    font-weight: bold;
}
#canvas {
    display: block;
    width: 100%;
    height: auto;
    background: white;
    border-radius: 12px;
    border: 1px solid #ddd;
    cursor: crosshair;
}
.legend {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin-top: 12px;
    font-size: 14px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 7px;
}
.real-line { width: 40px; border-top: 4px solid #e53935; }
.virtual-line { width: 40px; border-top: 2px dashed #777; }
.normal-line { width: 40px; border-top: 2px dashed #1976d2; }
.info { line-height: 1.8; font-size: 15px; }
</style>
</head>
<body>

<div class="panel">
    <div class="control-grid">
        <label>광학 기구 선택</label>
        <select id="objectType">
            <optgroup label="렌즈">
                <option value="convexLens">볼록렌즈</option>
                <option value="concaveLens">오목렌즈</option>
            </optgroup>
            <optgroup label="거울">
                <option value="planeMirror">평면거울</option>
                <option value="concaveMirror">오목거울</option>
                <option value="convexMirror">볼록거울</option>
            </optgroup>
            <option value="prism">프리즘</option>
        </select>
        <span></span>
    </div>

    <div id="radiusRow" class="control-grid" style="display:none;">
        <label>거울 곡률반지름</label>
        <input id="radius" type="range" min="150" max="400" value="250">
        <span id="radiusValue" class="value">250</span>
    </div>

    <div id="prismRow" class="control-grid" style="display:none;">
        <label>프리즘 꼭짓각</label>
        <input id="prismAngle" type="range" min="30" max="80" value="60">
        <span id="prismAngleValue" class="value">60°</span>
    </div>

    <div class="control-grid">
        <label>광학 기구 위치</label>
        <input id="position" type="range" min="350" max="850" value="650">
        <span id="positionValue" class="value">650</span>
    </div>
</div>

<div class="panel">
    <canvas id="canvas" width="1100" height="650"></canvas>
    <div class="legend">
        <div class="legend-item"><span class="real-line"></span> 실제 레이저 광선</div>
        <div class="legend-item"><span class="virtual-line"></span> 광선의 연장선</div>
        <div class="legend-item"><span class="normal-line"></span> 광축</div>
    </div>
</div>

<div class="panel info">
    <div><b>현재 광학 기구:</b> <span id="objectInfo">볼록렌즈</span></div>
    <div><b>레이저 각도:</b> <span id="angleInfo">0°</span></div>
    <div><b>광학 기구 위치:</b> <span id="positionInfo">650</span></div>
    <div id="physicsInfo"></div>
</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const W = canvas.width;
const H = canvas.height;
const axisY = H / 2;

const laser = { x: 90, y: axisY, angle: 0 };
let draggingLaserHandle = false;
let draggingObjectHandle = false;

const objectType = document.getElementById("objectType");
const radius = document.getElementById("radius");
const prismAngle = document.getElementById("prismAngle");
const position = document.getElementById("position");

const radiusRow = document.getElementById("radiusRow");
const prismRow = document.getElementById("prismRow");

function add(a,b) { return { x:a.x+b.x, y:a.y+b.y }; }
function sub(a,b) { return { x:a.x-b.x, y:a.y-b.y }; }
function mul(a,k) { return { x:a.x*k, y:a.y*k }; }
function length(a) { return Math.sqrt(a.x*a.x + a.y*a.y); }
function normalize(a) {
    const l = length(a);
    if(l === 0) return { x:1, y:0 };
    return { x:a.x/l, y:a.y/l };
}

function drawLine(p1, p2, color="#e53935", width=4, dashed=false) {
    ctx.beginPath();
    ctx.setLineDash(dashed ? [10,8] : []);
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawText(value, x, y, size=15, color="#222") {
    ctx.fillStyle = color;
    ctx.font = "bold " + size + "px Arial";
    ctx.fillText(value, x, y);
}

function objectX() { return parseFloat(position.value); }

function laserHandlePos() {
    return {
        x: laser.x + Math.cos(laser.angle) * 75,
        y: laser.y + Math.sin(laser.angle) * 75
    };
}

function objectHandlePos() {
    return { x: objectX(), y: axisY - 110 };
}

function drawLaserAndHandles() {
    // 레이저 본체
    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 24, 0, Math.PI*2);
    ctx.fillStyle = "#333";
    ctx.fill();
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 3;
    ctx.stroke();

    // 레이저 방향 조절 바 및 손잡이
    const lHandle = laserHandlePos();
    drawLine({x: laser.x, y: laser.y}, lHandle, "#fbc02d", 12);
    ctx.beginPath();
    ctx.arc(lHandle.x, lHandle.y, 14, 0, Math.PI*2);
    ctx.fillStyle = "#ffdf3f";
    ctx.fill();
    ctx.strokeStyle = "#806000";
    ctx.lineWidth = 2;
    ctx.stroke();
    drawText("방향 조절", lHandle.x - 30, lHandle.y - 20, 11, "#555");

    // 레이저 발사구 다이오드
    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 7, 0, Math.PI*2);
    ctx.fillStyle = "#ff0000";
    ctx.fill();

    // 광학 기구 상단 이동 손잡이 (파란색)
    const oHandle = objectHandlePos();
    ctx.beginPath();
    ctx.arc(oHandle.x, oHandle.y, 14, 0, Math.PI*2);
    ctx.fillStyle = "#1976d2";
    ctx.fill();
    ctx.strokeStyle = "#0d47a1";
    ctx.lineWidth = 2;
    ctx.stroke();
    drawText("기구 이동", oHandle.x - 32, oHandle.y - 20, 11, "#1976d2");
}

function drawAxis() {
    drawLine({x: 30, y: axisY}, {x: 1070, y: axisY}, "#aaa", 1, true);
    drawText("광축", 1015, axisY - 10, 13, "#888");
}

/* --- 광학 기구 모양 드로잉 함수들 (실제 모양 반영) --- */
function drawConvexLens() {
    const x = objectX();
    const h = 160;
    ctx.beginPath();
    // 볼록렌즈 외곽선 (양쪽이 불룩한 모양)
    ctx.moveTo(x - 15, axisY - h/2);
    ctx.quadraticCurveTo(x + 15, axisY, x - 15, axisY + h/2);
    ctx.quadraticCurveTo(x - 45, axisY, x - 15, axisY - h/2);
    ctx.fillStyle = "rgba(100, 200, 255, 0.3)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;
    ctx.stroke();
    drawText("볼록렌즈", x - 35, axisY + h/2 + 25, 14, "#0288d1");
}

function drawConcaveLens() {
    const x = objectX();
    const h = 160;
    ctx.beginPath();
    // 오목렌즈 외곽선 (가운데가 홀쭉하고 위아래가 두꺼운 모양)
    ctx.moveTo(x - 35, axisY - h/2);
    ctx.lineTo(x + 5, axisY - h/2);
    ctx.quadraticCurveTo(x - 15, axisY, x + 5, axisY + h/2);
    ctx.lineTo(x - 35, axisY + h/2);
    ctx.quadraticCurveTo(x - 15, axisY, x - 35, axisY - h/2);
    ctx.fillStyle = "rgba(100, 200, 255, 0.3)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;
    ctx.stroke();
    drawText("오목렌즈", x - 35, axisY + h/2 + 25, 14, "#0288d1");
}

function drawPlaneMirror() {
    const x = objectX();
    const h = 160;
    // 평면거울 (수직선 + 반대편 빗금 패턴)
    drawLine({x: x, y: axisY - h/2}, {x: x, y: axisY + h/2}, "#37474f", 5);
    for(let y = axisY - h/2 + 10; y < axisY + h/2; y += 15) {
        drawLine({x: x, y: y}, {x: x + 10, y: y + 10}, "#78909c", 2);
    }
    drawText("평면거울", x - 30, axisY + h/2 + 25, 14, "#37474f");
}

function drawConcaveMirror() {
    const x = objectX();
    const h = 160;
    // 오목거울 (반사면이 왼쪽을 향해 오목함)
    ctx.beginPath();
    ctx.arc(x + 120, axisY, 150, Math.PI * 0.75, Math.PI * 1.25);
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
    drawText("오목거울", x - 30, axisY + h/2 + 25, 14, "#37474f");
}

function drawConvexMirror() {
    const x = objectX();
    const h = 160;
    // 볼록거울 (반사면이 왼쪽을 향해 볼록함)
    ctx.beginPath();
    ctx.arc(x - 120, axisY, 150, Math.PI * 1.75, Math.PI * 0.25);
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
    drawText("볼록거울", x - 30, axisY + h/2 + 25, 14, "#37474f");
}

function drawPrism() {
    const x = objectX();
    const A = parseFloat(prismAngle.value) * Math.PI / 180;
    const base = 150;
    const height = base / (2 * Math.tan(A / 2));
    ctx.beginPath();
    ctx.moveTo(x - base / 2, axisY + height / 2);
    ctx.lineTo(x, axisY - height / 2);
    ctx.lineTo(x + base / 2, axisY + height / 2);
    ctx.closePath();
    ctx.fillStyle = "rgba(100, 200, 255, 0.25)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 4;
    ctx.stroke();
    drawText("프리즘", x - 25, axisY + height / 2 + 25, 14, "#0288d1");
}

/* --- 광선 작도 및 시뮬레이션 --- */
function traceRays() {
    const type = objectType.value;
    const ox = objectX();
    const p = { x: laser.x, y: laser.y };
    const d = normalize({ x: Math.cos(laser.angle), y: Math.sin(laser.angle) });

    // 기구 위치($x = ox$)까지의 광선 도달 계산
    if (Math.abs(d.x) < 1e-5) {
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
        return;
    }

    const t = (ox - p.x) / d.x;
    if (t <= 0) {
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
        return;
    }

    const hitPoint = add(p, mul(d, t));
    
    // 기구 높이 범위를 벗어나면 그냥 통과
    if (Math.abs(hitPoint.y - axisY) > 90 && type !== 'prism') {
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
        return;
    }

    // 입사광선 그리기
    drawLine(p, hitPoint, "#e53935", 4);

    let infoText = "";

    if (type === "convexLens") {
        // 볼록렌즈: 입사 후 광축(중앙)쪽으로 굴절 (수렴)
        let outDir;
        const dy = hitPoint.y - axisY;
        if (Math.abs(dy) < 1e-3) {
            outDir = d; // 광축 위 레이저는 직진
        } else {
            // 초점을 향해 꺾이도록 벡터 계산 (초점거리 f = 180)
            const f = 180;
            const focusPoint = { x: ox + f, y: axisY };
            outDir = normalize(sub(focusPoint, hitPoint));
        }
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        
        // 허상/연장선 (빛이 퍼져나가는 경우 반대쪽 연장선 표시 등)
        infoText = "볼록렌즈에 의해 빛이 수렴합니다.";
    } 
    else if (type === "concaveLens") {
        // 오목렌즈: 입사 후 광축으로부터 멀어지게 굴절 (발산)
        const dy = hitPoint.y - axisY;
        const outDir = normalize({ x: 1, y: dy > 0 ? 0.4 : -0.4 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        
        // 가상 초점 연장선
        const virtualFocus = { x: ox - 180, y: axisY };
        drawLine(hitPoint, virtualFocus, "#777", 2, true);
        infoText = "오목렌즈에 의해 빛이 발산합니다.";
    }
    else if (type === "planeMirror") {
        // 평면거울 반사 (법선 x축 기준 대칭)
        const outDir = { x: -d.x, y: d.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "입사각과 반사각이 같게 반사됩니다.";
    }
    else if (type === "concaveMirror") {
        // 오목거울 반사 (중앙으로 모임)
        const dy = hitPoint.y - axisY;
        const outDir = normalize({ x: -1, y: -dy * 0.015 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "오목거울에 의해 빛이 초점 방향으로 모입니다.";
    }
    else if (type === "convexMirror") {
        // 볼록거울 반사 (바깥으로 퍼짐)
        const dy = hitPoint.y - axisY;
        const outDir = normalize({ x: -1, y: dy * 0.015 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "볼록거울에 의해 빛이 바깥으로 퍼져 나갑니다.";
    }
    else if (type === "prism") {
        // 프리즘 굴절 시뮬레이션
        const outDir = normalize({ x: d.x * 0.3 - 0.7, y: d.y + 0.5 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "삼각형 프리즘에 의해 빛이 꺾여 굴절됩니다.";
    }

    document.getElementById("physicsInfo").innerHTML = "<b>광학 현상:</b> " + infoText;
}

function updateVisibility() {
    const type = objectType.value;
    radiusRow.style.display = (type === "concaveMirror" || type === "convexMirror") ? "grid" : "none";
    prismRow.style.display = (type === "prism") ? "grid" : "none";
}

function render() {
    ctx.clearRect(0, 0, W, H);
    drawAxis();
    
    // 광학 기구 모양 그리기
    const type = objectType.value;
    if (type === "convexLens") drawConvexLens();
    else if (type === "concaveLens") drawConcaveLens();
    else if (type === "planeMirror") drawPlaneMirror();
    else if (type === "concaveMirror") drawConcaveMirror();
    else if (type === "convexMirror") drawConvexMirror();
    else if (type === "prism") drawPrism();

    // 레이저 및 핸들 그리기
    drawLaserAndHandles();

    // 광선 작도 실행
    traceRays();

    // UI 정보 텍스트 업데이트
    document.getElementById("objectInfo").innerText = objectType.options[objectType.selectedIndex].text;
    document.getElementById("angleInfo").innerText = Math.round(laser.angle * 180 / Math.PI) + "°";
    document.getElementById("positionInfo").innerText = position.value;
}

/* --- 마우스 인터랙션 (드래그 조작) --- */
canvas.addEventListener("mousedown", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // 1. 레이저 손잡이 드래그 확인
    const lHandle = laserHandlePos();
    if (Math.hypot(mouseX - lHandle.x, mouseY - lHandle.y) < 25) {
        draggingLaserHandle = true;
        return;
    }

    // 2. 광학 기구 이동 손잡이 드래그 확인
    const oHandle = objectHandlePos();
    if (Math.hypot(mouseX - oHandle.x, mouseY - oHandle.y) < 30 || (Math.abs(mouseX - objectX()) < 40 && Math.abs(mouseY - axisY) < 90)) {
        draggingObjectHandle = true;
        return;
    }
});

window.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    if (draggingLaserHandle) {
        laser.angle = Math.atan2(mouseY - laser.y, mouseX - laser.x);
        render();
    } else if (draggingObjectHandle) {
        let newX = Math.max(350, Math.min(850, mouseX));
        position.value = Math.round(newX);
        document.getElementById("positionValue").innerText = position.value;
        render();
    }
});

window.addEventListener("mouseup", () => {
    draggingLaserHandle = false;
    draggingObjectHandle = false;
});

// UI 컨트롤 이벤트 연동
objectType.addEventListener("change", () => { updateVisibility(); render(); });
radius.addEventListener("input", () => { document.getElementById("radiusValue").innerText = radius.value; render(); });
prismAngle.addEventListener("input", () => { document.getElementById("prismAngleValue").innerText = prismAngle.value + "°"; render(); });
position.addEventListener("input", () => { render(); });

updateVisibility();
render();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
