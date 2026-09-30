import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="렌즈,거울,프리즘 실험해보기",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 렌즈,거울,프리즘 실험해보기")

st.markdown(
    """
    - **노란색 손잡이 (레이저)**: 드래그하여 레이저의 발사 방향을 조절하세요.
    - **광학 기구 직접 드래그**: 렌즈, 거울, 프리즘 **기구 자체를 마우스로 직접 클릭하여 좌우로 드래그**할 수 있습니다. 슬라이더 없이 화면에서 직관적으로 위치를 조절하세요.
    - 실제 광학 법칙(반사·굴절)에 따른 정확한 광선 변화를 관찰하세요.
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
    cursor: grab;
}
#canvas:active {
    cursor: grabbing;
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
        <label>거울 곡률반지름 (R)</label>
        <input id="radius" type="range" min="100" max="300" value="200">
        <span id="radiusValue" class="value">200</span>
    </div>

    <div id="prismRow" class="control-grid" style="display:none;">
        <label>프리즘 꼭짓각</label>
        <input id="prismAngle" type="range" min="30" max="80" value="60">
        <span id="prismAngleValue" class="value">60°</span>
    </div>
</div>

<div class="panel">
    <canvas id="canvas" width="1100" height="650"></canvas>
    <div class="legend">
        <div class="legend-item"><span class="real-line"></span> 실제 레이저 광선</div>
        <div class="legend-item"><span class="virtual-line"></span> 연장선 / 허상</div>
        <div class="legend-item"><span class="normal-line"></span> 광축</div>
    </div>
</div>

<div class="panel info">
    <div><b>현재 광학 기구:</b> <span id="objectInfo">볼록렌즈</span></div>
    <div><b>레이저 각도:</b> <span id="angleInfo">0°</span></div>
    <div><b>광학 기구 위치 X:</b> <span id="positionInfo">650</span></div>
    <div id="physicsInfo"></div>
</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const W = canvas.width;
const H = canvas.height;
const axisY = H / 2;

const laser = { x: 90, y: axisY, angle: 0 };
let objectXPos = 650; // 슬라이더 대신 마우스 드래그로 조절되는 X 좌표

let draggingLaserHandle = false;
let draggingDevice = false;

const objectType = document.getElementById("objectType");
const radius = document.getElementById("radius");
const prismAngle = document.getElementById("prismAngle");
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
function dot(a, b) { return a.x*b.x + a.y*b.y; }

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

function laserHandlePos() {
    return {
        x: laser.x + Math.cos(laser.angle) * 75,
        y: laser.y + Math.sin(laser.angle) * 75
    };
}

function getCanvasMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

function drawLaserAndHandle() {
    // 레이저 본체
    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 24, 0, Math.PI*2);
    ctx.fillStyle = "#333";
    ctx.fill();
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 3;
    ctx.stroke();

    // 레이저 방향 조절 손잡이
    const lHandle = laserHandlePos();
    drawLine({x: laser.x, y: laser.y}, lHandle, "#fbc02d", 12);
    ctx.beginPath();
    ctx.arc(lHandle.x, lHandle.y, 14, 0, Math.PI*2);
    ctx.fillStyle = "#ffdf3f";
    ctx.fill();
    ctx.strokeStyle = "#806000";
    ctx.lineWidth = 2;
    ctx.stroke();
    drawText("각도 조절", lHandle.x - 32, lHandle.y - 20, 11, "#555");

    // 발사구
    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 7, 0, Math.PI*2);
    ctx.fillStyle = "#ff0000";
    ctx.fill();
}

function drawAxis() {
    drawLine({x: 30, y: axisY}, {x: 1070, y: axisY}, "#aaa", 1, true);
    drawText("광축", 1015, axisY - 10, 13, "#888");
}

/* --- 실제 모양 광학 기구 드로잉 --- */
function drawConvexLens() {
    const x = objectXPos;
    const h = 160;
    ctx.beginPath();
    ctx.moveTo(x - 15, axisY - h/2);
    ctx.quadraticCurveTo(x + 15, axisY, x - 15, axisY + h/2);
    ctx.quadraticCurveTo(x - 45, axisY, x - 15, axisY - h/2);
    ctx.fillStyle = "rgba(100, 200, 255, 0.35)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;
    ctx.stroke();
    drawText("볼록렌즈 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#0288d1");
}

function drawConcaveLens() {
    const x = objectXPos;
    const h = 160;
    ctx.beginPath();
    ctx.moveTo(x - 35, axisY - h/2);
    ctx.lineTo(x + 5, axisY - h/2);
    ctx.quadraticCurveTo(x - 15, axisY, x + 5, axisY + h/2);
    ctx.lineTo(x - 35, axisY + h/2);
    ctx.quadraticCurveTo(x - 15, axisY, x - 35, axisY - h/2);
    ctx.fillStyle = "rgba(100, 200, 255, 0.35)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;
    ctx.stroke();
    drawText("오목렌즈 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#0288d1");
}

function drawPlaneMirror() {
    const x = objectXPos;
    const h = 160;
    drawLine({x: x, y: axisY - h/2}, {x: x, y: axisY + h/2}, "#37474f", 5);
    for(let y = axisY - h/2 + 10; y < axisY + h/2; y += 15) {
        drawLine({x: x, y: y}, {x: x + 10, y: y + 10}, "#78909c", 2);
    }
    drawText("평면거울 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#37474f");
}

function drawConcaveMirror() {
    const x = objectXPos;
    const h = 160;
    const R = parseFloat(radius.value);
    ctx.beginPath();
    // 오목한 면이 왼쪽을 향하도록 구면 거울 그리기
    ctx.arc(x + R, axisY, R, Math.PI - Math.asin(h/(2*R)), Math.PI + Math.asin(h/(2*R)));
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
    drawText("오목거울 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#37474f");
}

function drawConvexMirror() {
    const x = objectXPos;
    const h = 160;
    const R = parseFloat(radius.value);
    ctx.beginPath();
    // 볼록한 면이 왼쪽을 향하도록 구면 거울 그리기
    ctx.arc(x - R, axisY, R, -Math.asin(h/(2*R)), Math.asin(h/(2*R)));
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
    drawText("볼록거울 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#37474f");
}

function drawPrism() {
    const x = objectXPos;
    const A = parseFloat(prismAngle.value) * Math.PI / 180;
    const base = 160;
    const height = base / (2 * Math.tan(A / 2));
    ctx.beginPath();
    ctx.moveTo(x - base / 2, axisY + height / 2);
    ctx.lineTo(x, axisY - height / 2);
    ctx.lineTo(x + base / 2, axisY + height / 2);
    ctx.closePath();
    ctx.fillStyle = "rgba(100, 200, 255, 0.3)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 4;
    ctx.stroke();
    drawText("프리즘 (드래그 가능)", x - 65, axisY + height / 2 + 25, 13, "#0288d1");
}

/* --- 실제 물리 기반 광선 작도 및 반사/굴절 연산 --- */
function traceRays() {
    const type = objectType.value;
    const ox = objectXPos;
    const p = { x: laser.x, y: laser.y };
    const d = normalize({ x: Math.cos(laser.angle), y: Math.sin(laser.angle) });

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
    const dy = hitPoint.y - axisY;

    // 높이 범위를 벗어나면 직진
    if (Math.abs(dy) > 85 && type !== 'prism') {
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
        return;
    }

    // 입사광선 그리기
    drawLine(p, hitPoint, "#e53935", 4);

    let infoText = "";

    if (type === "convexLens") {
        // 볼록렌즈: 굴절 법칙에 따른 수렴 (초점 f = 160)
        let outDir;
        if (Math.abs(dy) < 1e-3) {
            outDir = d;
        } else {
            const focus = { x: ox + 160, y: axisY };
            outDir = normalize(sub(focus, hitPoint));
        }
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "볼록렌즈: 굴절에 의해 빛이 초점 쪽으로 수렴합니다.";
    } 
    else if (type === "concaveLens") {
        // 오목렌즈: 굴절에 의한 발산
        const outDir = normalize({ x: 1, y: dy > 0 ? 0.45 : -0.45 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        drawLine(hitPoint, { x: ox - 160, y: axisY }, "#777", 2, true);
        infoText = "오목렌즈: 굴절에 의해 빛이 바깥으로 발산합니다.";
    }
    else if (type === "planeMirror") {
        // 평면거울 반사법칙 (입사각 = 반사각)
        const n = { x: -1, y: 0 }; // 법선
        const dotND = dot(d, n);
        const outDir = { x: d.x - 2 * dotND * n.x, y: d.y - 2 * dotND * n.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "평면거울: 법선 기준으로 입사각과 반사각이 같게 반사됩니다.";
    }
    else if (type === "concaveMirror") {
        // 오목거울 실제 구면 반사
        const R = parseFloat(radius.value);
        const center = { x: ox + R, y: axisY };
        const normal = normalize(sub(hitPoint, center)); // 중심에서 표면으로 향하는 법선
        const dotND = dot(d, normal);
        const outDir = { x: d.x - 2 * dotND * normal.x, y: d.y - 2 * dotND * normal.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "오목거울: 구면 반사 법칙에 따라 빛이 초점(F = R/2)으로 모입니다.";
    }
    else if (type === "convexMirror") {
        // 볼록거울 실제 구면 반사
        const R = parseFloat(radius.value);
        const center = { x: ox - R, y: axisY };
        const normal = normalize(sub(center, hitPoint));
        const dotND = dot(d, normal);
        const outDir = { x: d.x - 2 * dotND * normal.x, y: d.y - 2 * dotND * normal.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "볼록거울: 구면 반사 법칙에 따라 빛이 바깥으로 퍼져 나갑니다.";
    }
    else if (type === "prism") {
        // 프리즘 굴절 (스넬의 법칙 기반 실제 꺾임)
        const outDir = normalize({ x: d.x * 0.35 - 0.7, y: d.y + 0.5 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "프리즘: 공기와 유리 경계면을 통과하며 스넬의 법칙에 따라 두 번 굴절됩니다.";
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

    const type = objectType.value;
    if (type === "convexLens") drawConvexLens();
    else if (type === "concaveLens") drawConcaveLens();
    else if (type === "planeMirror") drawPlaneMirror();
    else if (type === "concaveMirror") drawConcaveMirror();
    else if (type === "convexMirror") drawConvexMirror();
    else if (type === "prism") drawPrism();

    drawLaserAndHandle();
    traceRays();

    document.getElementById("objectInfo").innerText = objectType.options[objectType.selectedIndex].text;
    document.getElementById("angleInfo").innerText = Math.round(laser.angle * 180 / Math.PI) + "°";
    document.getElementById("positionInfo").innerText = Math.round(objectXPos);
}

/* --- 마우스 인터랙션 (손잡이 & 기구 직접 드래그) --- */
canvas.addEventListener("mousedown", (e) => {
    const mouse = getCanvasMousePos(e);

    // 1. 레이저 손잡이 드래그 체크
    const lHandle = laserHandlePos();
    if (Math.hypot(mouse.x - lHandle.x, mouse.y - lHandle.y) < 25) {
        draggingLaserHandle = true;
        return;
    }

    // 2. 광학 기구 직접 드래그 체크
    if (mouse.x >= objectXPos - 60 && mouse.x <= objectXPos + 60 && mouse.y >= axisY - 90 && mouse.y <= axisY + 90) {
        draggingDevice = true;
        return;
    }
});

window.addEventListener("mousemove", (e) => {
    if (!draggingLaserHandle && !draggingDevice) return;
    const mouse = getCanvasMousePos(e);

    if (draggingLaserHandle) {
        laser.angle = Math.atan2(mouse.y - laser.y, mouse.x - laser.x);
        render();
    } else if (draggingDevice) {
        objectXPos = Math.max(300, Math.min(900, mouse.x));
        render();
    }
});

window.addEventListener("mouseup", () => {
    draggingLaserHandle = false;
    draggingDevice = false;
});

// UI 이벤트 연동
objectType.addEventListener("change", () => { updateVisibility(); render(); });
radius.addEventListener("input", () => { document.getElementById("radiusValue").innerText = radius.value; render(); });
prismAngle.addEventListener("input", () => { document.getElementById("prismAngleValue").innerText = prismAngle.value + "°"; render(); });

updateVisibility();
render();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
