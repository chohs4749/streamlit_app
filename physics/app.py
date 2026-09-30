import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="레이저 광학 시뮬레이터",
    page_icon="🔴",
    layout="wide"
)

st.title("🔴 레이저 광학 시뮬레이터 (드래그 지원)")

st.markdown(
    """
    - **레이저 손잡이**: 드래그하여 입사 방향을 바꿀 수 있습니다.
    - **광학 기구 (렌즈/거울/프리즘)**: 캔버스 위에서 **직접 마우스로 드래그**하여 위치를 좌우로 이동할 수 있습니다. (슬라이더와도 연동됩니다.)
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
        <label>광학 기구</label>
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

    <div id="materialRow" class="control-grid">
        <label>렌즈 재질</label>
        <select id="material">
            <option value="1.49">아크릴 (n = 1.49)</option>
            <option value="1.52" selected>일반 유리 (n = 1.52)</option>
            <option value="1.62">고굴절 유리 (n = 1.62)</option>
        </select>
        <span id="materialValue" class="value">n = 1.52</span>
    </div>

    <div id="thicknessRow" class="control-grid">
        <label>렌즈 중심 두께</label>
        <input id="thickness" type="range" min="30" max="140" value="70">
        <span id="thicknessValue" class="value">70</span>
    </div>

    <div id="radiusRow" class="control-grid">
        <label>거울 곡률반지름</label>
        <input id="radius" type="range" min="180" max="500" value="300">
        <span id="radiusValue" class="value">300</span>
    </div>

    <div id="prismRow" class="control-grid" style="display:none;">
        <label>프리즘 꼭짓각</label>
        <input id="prismAngle" type="range" min="30" max="80" value="60">
        <span id="prismAngleValue" class="value">60°</span>
    </div>

    <div id="prismMaterialRow" class="control-grid" style="display:none;">
        <label>프리즘 굴절률</label>
        <input id="prismIndex" type="range" min="1.10" max="2.00" step="0.01" value="1.52">
        <span id="prismIndexValue" class="value">1.52</span>
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
        <div class="legend-item"><span class="real-line"></span> 실제 광선</div>
        <div class="legend-item"><span class="virtual-line"></span> 광선의 연장 / 허상</div>
        <div class="legend-item"><span class="normal-line"></span> 법선</div>
    </div>
</div>

<div class="panel info">
    <div><b>현재 광학 기구:</b> <span id="objectInfo">볼록렌즈</span></div>
    <div><b>레이저 방향:</b> <span id="angleInfo">0°</span></div>
    <div><b>광학 기구 위치:</b> <span id="positionInfo">650</span></div>
    <div id="physicsInfo"></div>
    <div><b>광선 작도:</b> <span id="imageInfo"></span></div>
</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const W = canvas.width;
const H = canvas.height;
const axisY = H / 2;

const laser = { x: 90, y: axisY, angle: 0 };
let draggingLaserHandle = false;
let draggingObject = false;

const objectType = document.getElementById("objectType");
const material = document.getElementById("material");
const thickness = document.getElementById("thickness");
const radius = document.getElementById("radius");
const prismAngle = document.getElementById("prismAngle");
const position = document.getElementById("position");
const prismIndex = document.getElementById("prismIndex");

const materialRow = document.getElementById("materialRow");
const thicknessRow = document.getElementById("thicknessRow");
const radiusRow = document.getElementById("radiusRow");
const prismRow = document.getElementById("prismRow");
const prismMaterialRow = document.getElementById("prismMaterialRow");

function add(a,b) { return { x:a.x+b.x, y:a.y+b.y }; }
function sub(a,b) { return { x:a.x-b.x, y:a.y-b.y }; }
function mul(a,k) { return { x:a.x*k, y:a.y*k }; }
function dot(a,b) { return a.x*b.x + a.y*b.y; }
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

function drawText(value, x, y, size=16, color="#222") {
    ctx.fillStyle = color;
    ctx.font = "bold " + size + "px Arial";
    ctx.fillText(value, x, y);
}

function objectX() { return parseFloat(position.value); }
function handlePosition() {
    return {
        x: laser.x + Math.cos(laser.angle) * 75,
        y: laser.y + Math.sin(laser.angle) * 75
    };
}

function drawLaser() {
    const handle = handlePosition();
    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 24, 0, Math.PI*2);
    ctx.fillStyle = "#333";
    ctx.fill();
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 3;
    ctx.stroke();

    drawLine({x: laser.x, y: laser.y}, handle, "#fbc02d", 14);

    ctx.beginPath();
    ctx.arc(handle.x, handle.y, 15, 0, Math.PI*2);
    ctx.fillStyle = "#ffdf3f";
    ctx.fill();
    ctx.strokeStyle = "#806000";
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 7, 0, Math.PI*2);
    ctx.fillStyle = "#ff0000";
    ctx.fill();
    drawText("방향 조절", handle.x - 30, handle.y - 22, 12, "#555");
}

function drawAxis() {
    drawLine({x: 30, y: axisY}, {x: 1070, y: axisY}, "#aaa", 1, true);
    drawText("광축", 1015, axisY - 10, 13, "#888");
}

/* 프리즘 드래그 영역 판정용 꼭짓점 */
function prismVertices() {
    const x = objectX();
    const A = parseFloat(prismAngle.value) * Math.PI / 180;
    const base = 300;
    const height = base / (2 * Math.tan(A / 2));
    return [
        { x: x - base / 2, y: axisY + height / 2 },
        { x: x, y: axisY - height / 2 },
        { x: x + base / 2, y: axisY + height / 2 }
    ];
}

function drawPrism() {
    const verts = prismVertices();
    ctx.beginPath();
    ctx.moveTo(verts[0].x, verts[0].y);
    ctx.lineTo(verts[1].x, verts[1].y);
    ctx.lineTo(verts[2].x, verts[2].y);
    ctx.closePath();
    ctx.fillStyle = "rgba(100, 200, 255, 0.25)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 4;
    ctx.stroke();
    drawText("프리즘 (드래그 가능)", objectX() - 65, axisY + 45, 14, "#0288d1");
}

function updateVisibility() {
    const type = objectType.value;
    materialRow.style.display = (type === "convexLens" || type === "concaveLens") ? "grid" : "none";
    thicknessRow.style.display = (type === "convexLens" || type === "concaveLens") ? "grid" : "none";
    radiusRow.style.display = (type === "concaveMirror" || type === "convexMirror") ? "grid" : "none";
    prismRow.style.display = (type === "prism") ? "grid" : "none";
    prismMaterialRow.style.display = (type === "prism") ? "grid" : "none";
}

function render() {
    ctx.clearRect(0, 0, W, H);
    drawAxis();
    drawLaser();

    const type = objectType.value;
    if(type === "prism") {
        drawPrism();
    } else {
        // 일반 렌즈/거울 대표 표시 (위치에 바 형태 핸들 제공)
        const ox = objectX();
        ctx.fillStyle = "rgba(25, 118, 210, 0.2)";
        ctx.fillRect(ox - 15, axisY - 80, 30, 160);
        ctx.strokeStyle = "#1976d2";
        ctx.lineWidth = 3;
        ctx.strokeRect(ox - 15, axisY - 80, 30, 160);
        drawText(objectType.options[objectType.selectedIndex].text + " (드래그)", ox - 55, axisY - 95, 13, "#1976d2");
    }

    document.getElementById("objectInfo").innerText = objectType.options[objectType.selectedIndex].text;
    document.getElementById("angleInfo").innerText = Math.round(laser.angle * 180 / Math.PI) + "°";
    document.getElementById("positionInfo").innerText = position.value;
}

// 마우스 인터랙션 (드래그 구현)
canvas.addEventListener("mousedown", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // 1. 레이저 손잡이 드래그 판정
    const handle = handlePosition();
    if(Math.hypot(mouseX - handle.x, mouseY - handle.y) < 25) {
        draggingLaserHandle = true;
        return;
    }

    // 2. 광학 기구(렌즈/거울/프리즘) 직접 드래그 판정
    const ox = objectX();
    if(mouseX >= ox - 40 && mouseX <= ox + 40 && mouseY >= axisY - 90 && mouseY <= axisY + 90) {
        draggingObject = true;
    }
});

window.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    if(draggingLaserHandle) {
        laser.angle = Math.atan2(mouseY - laser.y, mouseX - laser.x);
        render();
    } else if(draggingObject) {
        // 캔버스 범위 내로 위치 제한 (350 ~ 850)
        let newX = Math.max(350, Math.min(850, mouseX));
        position.value = Math.round(newX);
        document.getElementById("positionValue").innerText = position.value;
        render();
    }
});

window.addEventListener("mouseup", () => {
    draggingLaserHandle = false;
    draggingObject = false;
});

// UI 컨트롤 이벤트 연동
objectType.addEventListener("change", () => { updateVisibility(); render(); });
material.addEventListener("input", () => { document.getElementById("materialValue").innerText = "n = " + material.value; render(); });
thickness.addEventListener("input", () => { document.getElementById("thicknessValue").innerText = thickness.value; render(); });
radius.addEventListener("input", () => { document.getElementById("radiusValue").innerText = radius.value; render(); });
prismAngle.addEventListener("input", () => { document.getElementById("prismAngleValue").innerText = prismAngle.value + "°"; render(); });
prismIndex.addEventListener("input", () => { document.getElementById("prismIndexValue").innerText = prismIndex.value; render(); });
position.addEventListener("input", () => { render(); });

updateVisibility();
render();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
