import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="레이저 광학 시뮬레이터",
    page_icon="🔴",
    layout="wide"
)

st.title("🔴 레이저 광학 시뮬레이터 (마우스 드래그 완벽 지원)")

st.markdown(
    """
    - **노란색 손잡이 (레이저)**: 드래그하여 레이저의 발사 방향을 조절하세요.
    - **광학 기구 직접 드래그**: 렌즈, 거울, 프리즘 **기구 자체를 마우스로 직접 클릭하여 좌우로 드래그**할 수 있습니다.
    - 실제 모양(볼록/오목/삼각형)과 정확한 반사 및 굴절 광선을 관찰하세요.
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
        <div class="legend-item"><span class="virtual-line"></span> 연장선 / 허상</div>
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
let draggingDevice = false;

const objectType = document.getElementById("objectType");
const prismAngle = document.getElementById("prismAngle");
const position = document.getElementById("position");
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

// 마우스 좌표를 캔버스 내부 실제 픽셀 좌표로 정확히 변환
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

    // 레이저 방향 조절 노란 손잡이
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

    // 레이저 발사구
    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 7, 0, Math.PI*2);
    ctx.fillStyle = "#ff0000";
    ctx.fill();
}

function drawAxis() {
    drawLine({x: 30, y: axisY}, {x: 1070, y: axisY}, "#aaa", 1, true);
    drawText("광축", 1015, axisY - 10, 13, "#888");
}

/* --- 실제 광학 기구 외형 그리기 --- */
function drawConvexLens() {
    const x = objectX();
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
    const x = objectX();
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
    const x = objectX();
    const h = 160;
    drawLine({x: x, y: axisY - h/2}, {x: x, y: axisY + h/2}, "#37474f", 5);
    for(let y = axisY - h/2 + 10; y < axisY + h/2; y += 15) {
        drawLine({x: x, y: y}, {x: x + 10, y: y + 10}, "#78909c", 2);
    }
    drawText("평면거울 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#37474f");
}

function drawConcaveMirror() {
    const x = objectX();
    const h = 160;
    ctx.beginPath();
    ctx.arc(x + 120, axisY, 150, Math.PI * 0.75, Math.PI * 1.25);
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
    drawText("오목거울 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#37474f");
}

function drawConvexMirror() {
    const x = objectX();
    const h = 160;
    ctx.beginPath();
    ctx.arc(x - 120, axisY, 150, Math.PI * 1.75, Math.PI * 0.25);
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
    drawText("볼록거울 (드래그 가능)", x - 75, axisY + h/2 + 25, 13, "#37474f");
}

function drawPrism() {
    const x = objectX();
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

/* --- 광선 작도 및 물리 연산 --- */
function traceRays() {
    const type = objectType.value;
    const ox = objectX();
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
    
    // 기구 세로 범위를 벗어나면 직진
    if (Math.abs(hitPoint.y - axisY) > 85 && type !== 'prism') {
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
        return;
    }

    // 입사광선
    drawLine(p, hitPoint, "#e53935", 4);

    let infoText = "";

    if (type === "convexLens") {
        const dy = hitPoint.y - axisY;
        let outDir;
        if (Math.abs(dy) < 1e-3) {
            outDir = d;
        } else {
            const focus = { x: ox + 180, y: axisY };
            outDir = normalize(sub(focus, hitPoint));
        }
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "볼록렌즈: 입사광이 초점을 향해 수렴합니다.";
    } 
    else if (type === "concaveLens") {
        const dy = hitPoint.y - axisY;
        const outDir = normalize({ x: 1, y: dy > 0 ? 0.45 : -0.45 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        drawLine(hitPoint, { x: ox - 180, y: axisY }, "#777", 2, true);
        infoText = "오목렌즈: 입사광이 퍼져나갑니다 (발산).";
    }
    else if (type === "planeMirror") {
        const outDir = { x: -d.x, y: d.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "평면거울: 입사각과 반사각이 같게 반사됩니다.";
    }
    else if (type === "concaveMirror") {
        const dy = hitPoint.y - axisY;
        const outDir = normalize({ x: -1, y: -dy * 0.02 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "오목거울: 반사광이 초점으로 모입니다.";
    }
    else if (type === "convexMirror") {
        const dy = hitPoint.y - axisY;
        const outDir = normalize({ x: -1, y: dy * 0.02 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "볼록거울: 반사광이 바깥쪽으로 퍼집니다.";
    }
    else if (type === "prism") {
        const outDir = normalize({ x: d.x * 0.3 - 0.75, y: d.y + 0.55 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        infoText = "프리즘: 삼각 경계면에서 굴절이 일어납니다.";
    }

    document.getElementById("physicsInfo").innerHTML = "<b>광학 현상:</b> " + infoText;
}

function updateVisibility() {
    const type = objectType.value;
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
    document.getElementById("positionInfo").innerText = position.value;
}

/* --- 마우스 드래그 이벤트 (좌우 위치 완벽 연동) --- */
canvas.addEventListener("mousedown", (e) => {
    const mouse = getCanvasMousePos(e);

    // 1. 레이저 손잡이 드래그 체크
    const lHandle = laserHandlePos();
    if (Math.hypot(mouse.x - lHandle.x, mouse.y - lHandle.y) < 25) {
        draggingLaserHandle = true;
        return;
    }

    // 2. 광학 기구 직접 드래그 체크 (기구 영역 클릭 시)
    const ox = objectX();
    if (mouse.x >= ox - 60 && mouse.x <= ox + 60 && mouse.y >= axisY - 90 && mouse.y <= axisY + 90) {
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
        let newX = Math.max(350, Math.min(850, mouse.x));
        position.value = Math.round(newX);
        document.getElementById("positionValue").innerText = position.value;
        render();
    }
});

window.addEventListener("mouseup", () => {
    draggingLaserHandle = false;
    draggingDevice = false;
});

// UI 컨트롤 이벤트 연동
objectType.addEventListener("change", () => { updateVisibility(); render(); });
prismAngle.addEventListener("input", () => { document.getElementById("prismAngleValue").innerText = prismAngle.value + "°"; render(); });
position.addEventListener("input", () => { render(); });

updateVisibility();
render();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
