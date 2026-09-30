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
    - **광학 기구 직접 드래그**: 렌즈, 거울, 프리즘 기구를 마우스로 직접 클릭하여 좌우로 이동할 수 있습니다.
    - 슬라이더를 통해 광학 기구의 크기와 곡률, 프리즘 각도를 세밀하게 조절해 보세요.
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

    <div class="control-grid">
        <label>기구 크기 (높이)</label>
        <input id="deviceSize" type="range" min="100" max="260" value="160">
        <span id="deviceSizeValue" class="value">160</span>
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
        <div class="legend-item"><span class="virtual-line"></span> 연장선 / 허상 (점선)</div>
        <div class="legend-item"><span class="normal-line"></span> 광축</div>
    </div>
</div>

<div class="panel info">
    <div><b>현재 광학 기구:</b> <span id="objectInfo">볼록렌즈</span></div>
    <div><b>레이저 각도:</b> <span id="angleInfo">0°</span></div>
    <div><b>기구 위치 X:</b> <span id="positionInfo">650</span></div>
    <div id="physicsInfo"></div>
</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const W = canvas.width;
const H = canvas.height;
const axisY = H / 2;

const laser = { x: 90, y: axisY, angle: 0 };
let objectXPos = 650;

let draggingLaserHandle = false;
let draggingDevice = false;

const objectType = document.getElementById("objectType");
const deviceSize = document.getElementById("deviceSize");
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

    // 레이저 방향 조절 손잡이 ("레이저"로 표기)
    const lHandle = laserHandlePos();
    drawLine({x: laser.x, y: laser.y}, lHandle, "#fbc02d", 12);
    ctx.beginPath();
    ctx.arc(lHandle.x, lHandle.y, 14, 0, Math.PI*2);
    ctx.fillStyle = "#ffdf3f";
    ctx.fill();
    ctx.strokeStyle = "#806000";
    ctx.lineWidth = 2;
    ctx.stroke();
    drawText("레이저", lHandle.x - 22, lHandle.y - 20, 11, "#555");

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

/* --- 실제 모양 광학 기구 드로잉 (이름 및 설명 제거) --- */
function drawConvexLens() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    ctx.beginPath();
    ctx.moveTo(x - 15, axisY - h/2);
    ctx.quadraticCurveTo(x + 15, axisY, x - 15, axisY + h/2);
    ctx.quadraticCurveTo(x - 45, axisY, x - 15, axisY - h/2);
    ctx.fillStyle = "rgba(100, 200, 255, 0.35)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;
    ctx.stroke();
}

function drawConcaveLens() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
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
}

function drawPlaneMirror() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    drawLine({x: x, y: axisY - h/2}, {x: x, y: axisY + h/2}, "#37474f", 5);
    for(let y = axisY - h/2 + 10; y < axisY + h/2; y += 15) {
        drawLine({x: x, y: y}, {x: x + 10, y: y + 10}, "#78909c", 2);
    }
}

function drawConcaveMirror() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    const R = parseFloat(radius.value);
    ctx.beginPath();
    ctx.arc(x + R, axisY, R, Math.PI - Math.asin(Math.min(1, h/(2*R))), Math.PI + Math.asin(Math.min(1, h/(2*R))));
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
}

function drawConvexMirror() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    const R = parseFloat(radius.value);
    ctx.beginPath();
    ctx.arc(x - R, axisY, R, -Math.asin(Math.min(1, h/(2*R))), Math.asin(Math.min(1, h/(2*R))));
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
}

function drawPrism() {
    const x = objectXPos;
    const A = parseFloat(prismAngle.value) * Math.PI / 180;
    const base = parseFloat(deviceSize.value);
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
}

/* --- 선분 교차 계산 함수 --- */
function getSegmentIntersection(p, d, a, b) {
    const v = sub(b, a);
    const cross = d.x * (-v.y) - d.y * (-v.x);
    if (Math.abs(cross) < 1e-6) return null;
    const ap = sub(a, p);
    const t = (ap.x * (-v.y) - ap.y * (-v.x)) / cross;
    const s = (d.x * ap.y - d.y * ap.x) / cross;
    if (t > 0 && s >= 0 && s <= 1) {
        return { t, s, point: add(p, mul(d, t)) };
    }
    return null;
}

/* --- Snell's Law 굴절 계산 함수 --- */
function refract(incident, normal, n1, n2) {
    let cosi = -dot(incident, normal);
    let etai = n1, etat = n2;
    let n = { x: normal.x, y: normal.y };
    if (cosi < 0) {
        cosi = -cosi;
        n = { x: -normal.x, y: -normal.y };
        etai = n2;
        etat = n1;
    }
    const eta = etai / etat;
    const k = 1 - eta * eta * (1 - cosi * cosi);
    if (k < 0) {
        // 전반사 시 반사 광선 반환
        return { ray: { x: incident.x - 2 * dot(incident, n) * n.x, y: incident.y - 2 * dot(incident, n) * n.y }, tir: true };
    }
    const rx = eta * incident.x + (eta * cosi - Math.sqrt(k)) * n.x;
    const ry = eta * incident.y + (eta * cosi - Math.sqrt(k)) * n.y;
    return { ray: normalize({ x: rx, y: ry }), tir: false };
}

/* --- 광선 작도 및 물리 연산 (점선 및 프리즘 실제 굴절 포함) --- */
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
    const hLimit = parseFloat(deviceSize.value) / 2;

    if (Math.abs(dy) > hLimit && type !== 'prism') {
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
        return;
    }

    // 입사광선
    drawLine(p, hitPoint, "#e53935", 4);

    let infoText = "";

    if (type === "convexLens") {
        let outDir;
        if (Math.abs(dy) < 1e-3) {
            outDir = d;
        } else {
            const focus = { x: ox + 160, y: axisY };
            outDir = normalize(sub(focus, hitPoint));
        }
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        // 초점 연장선 점선 추가
        drawLine(hitPoint, { x: ox + 160, y: axisY }, "#777", 2, true);
        infoText = "볼록렌즈: 굴절에 의해 빛이 초점 쪽으로 수렴하며 점선으로 초점 경로가 표시됩니다.";
    } 
    else if (type === "concaveLens") {
        const outDir = normalize({ x: 1, y: dy > 0 ? 0.45 : -0.45 });
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        // 허상 연장선 점선 추가
        drawLine(hitPoint, { x: ox - 160, y: axisY }, "#777", 2, true);
        infoText = "오목렌즈: 발산하는 빛의 허상 연장선이 점선으로 표시됩니다.";
    }
    else if (type === "planeMirror") {
        const n = { x: -1, y: 0 };
        const dotND = dot(d, n);
        const outDir = { x: d.x - 2 * dotND * n.x, y: d.y - 2 * dotND * n.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        // 거울 뒤쪽 가상 연장선 점선 추가
        drawLine(hitPoint, { x: ox - 100, y: hitPoint.y }, "#777", 2, true);
        infoText = "평면거울: 반사법칙에 따라 반사되며 뒤쪽에 가상 연장선(점선)이 생깁니다.";
    }
    else if (type === "concaveMirror") {
        const R = parseFloat(radius.value);
        const center = { x: ox + R, y: axisY };
        const normal = normalize(sub(hitPoint, center));
        const dotND = dot(d, normal);
        const outDir = { x: d.x - 2 * dotND * normal.x, y: d.y - 2 * dotND * normal.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        // 초점 점선 표시
        drawLine(hitPoint, { x: ox - R/2, y: axisY }, "#777", 2, true);
        infoText = "오목거울: 구면 반사에 의해 빛이 초점(F=R/2)으로 모입니다.";
    }
    else if (type === "convexMirror") {
        const R = parseFloat(radius.value);
        const center = { x: ox - R, y: axisY };
        const normal = normalize(sub(center, hitPoint));
        const dotND = dot(d, normal);
        const outDir = { x: d.x - 2 * dotND * normal.x, y: d.y - 2 * dotND * normal.y };
        drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
        // 거울 내부 허상 초점 점선
        drawLine(hitPoint, { x: ox + R/2, y: axisY }, "#777", 2, true);
        infoText = "볼록거울: 빛이 퍼져나가며 거울 뒤쪽 초점으로 모이는 듯한 연장선(점선)이 생깁니다.";
    }
    else if (type === "prism") {
        // 프리즘 정밀 굴절 (스넬의 법칙)
        const A = parseFloat(prismAngle.value) * Math.PI / 180;
        const base = parseFloat(deviceSize.value);
        const height = base / (2 * Math.tan(A / 2));
        
        const Vbl = { x: ox - base / 2, y: axisY + height / 2 };
        const Vtop = { x: ox, y: axisY - height / 2 };
        const Vbr = { x: ox + base / 2, y: axisY + height / 2 };

        // 1. 왼쪽 경계면 (Vbl -> Vtop) 교차 검사
        const inter1 = getSegmentIntersection(p, d, Vbl, Vtop);
        if (inter1) {
            drawLine(p, inter1.point, "#e53935", 4);
            
            // 왼쪽 면 법선 (바깥쪽 방향: 왼쪽 위를 향함)
            const vLeft = sub(Vtop, Vbl);
            let normal1 = normalize({ x: -vLeft.y, y: vLeft.x });
            if (dot(d, normal1) > 0) normal1 = { x: -normal1.x, y: -normal1.y };

            // 첫 번째 굴절 (공기 n=1.0 -> 유리 n=1.5)
            const ref1 = refract(d, normal1, 1.0, 1.5);
            const rRay1 = ref1.ray;

            // 2. 오른쪽 경계면 (Vtop -> Vbr) 또는 밑면 교차 검사
            const inter2 = getSegmentIntersection(inter1.point, rRay1, Vtop, Vbr);
            if (inter2) {
                // 내부 광선
                drawLine(inter1.point, inter2.point, "#e53935", 4);
                // 내부 진행 경로 점선
                drawLine(inter1.point, inter2.point, "#777", 1, true);

                // 오른쪽 면 법선
                const vRight = sub(Vbr, Vtop);
                let normal2 = normalize({ x: vRight.y, y: -vRight.x });
                if (dot(rRay1, normal2) > 0) normal2 = { x: -normal2.x, y: -normal2.y };

                // 두 번째 굴절 (유리 n=1.5 -> 공기 n=1.0)
                const ref2 = refract(rRay1, normal2, 1.5, 1.0);
                const rRay2 = ref2.ray;

                // 최종 출사 광선
                drawLine(inter2.point, add(inter2.point, mul(rRay2, 800)), "#e53935", 4);
                infoText = "프리즘: 스넬의 법칙에 따라 입사면과 출사면 두 번에 걸쳐 정확하게 굴절됩니다.";
            } else {
                drawLine(inter1.point, add(inter1.point, mul(rRay1, 800)), "#e53935", 4);
                infoText = "프리즘 내부 굴절 광선";
            }
        } else {
            drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
            infoText = "프리즘에 광선이 도달하지 않았습니다.";
        }
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

/* --- 마우스 인터랙션 --- */
canvas.addEventListener("mousedown", (e) => {
    const mouse = getCanvasMousePos(e);

    // 1. 레이저 손잡이 드래그 체크
    const lHandle = laserHandlePos();
    if (Math.hypot(mouse.x - lHandle.x, mouse.y - lHandle.y) < 25) {
        draggingLaserHandle = true;
        return;
    }

    // 2. 광학 기구 직접 드래그 체크
    const hLimit = parseFloat(deviceSize.value) / 2;
    if (mouse.x >= objectXPos - 60 && mouse.x <= objectXPos + 60 && mouse.y >= axisY - hLimit - 20 && mouse.y <= axisY + hLimit + 20) {
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
        objectXPos = Math.max(300, Math.min(950, mouse.x));
        render();
    }
});

window.addEventListener("mouseup", () => {
    draggingLaserHandle = false;
    draggingDevice = false;
});

// UI 이벤트 연동
objectType.addEventListener("change", () => { updateVisibility(); render(); });
deviceSize.addEventListener("input", () => { document.getElementById("deviceSizeValue").innerText = deviceSize.value; render(); });
radius.addEventListener("input", () => { document.getElementById("radiusValue").innerText = radius.value; render(); });
prismAngle.addEventListener("input", () => { document.getElementById("prismAngleValue").innerText = prismAngle.value + "°"; render(); });

updateVisibility();
render();
</script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
