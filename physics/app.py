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
    - **점선**: 굴절이나 반사가 일어나지 않고 직진했을 때의 원래 레이저 경로입니다.
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
.virtual-line { width: 40px; border-top: 2px dashed #ff9800; }
.axis-line { width: 40px; border-top: 2px dashed #aaa; }
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
        <input id="deviceSize" type="range" min="120" max="360" value="220">
        <span id="deviceSizeValue" class="value">220</span>
    </div>

    <div id="lensThicknessRow" class="control-grid">
        <label>렌즈 두께</label>
        <input id="lensThickness" type="range" min="20" max="70" value="40">
        <span id="lensThicknessValue" class="value">40</span>
    </div>

    <div id="radiusRow" class="control-grid" style="display:none;">
        <label>거울 곡률반지름 (R)</label>
        <input id="radius" type="range" min="100" max="350" value="220">
        <span id="radiusValue" class="value">220</span>
    </div>

    <div id="prismRow" class="control-grid" style="display:none;">
        <label>프리즘 꼭짓각</label>
        <input id="prismAngle" type="range" min="30" max="80" value="60">
        <span id="prismAngleValue" class="value">60°</span>
    </div>
</div>

<div class="panel">
    <canvas id="canvas" width="1100" height="680"></canvas>
    <div class="legend">
        <div class="legend-item"><span class="real-line"></span> 실제 레이저 광선 (굴절/반사)</div>
        <div class="legend-item"><span class="virtual-line"></span> 직진했을 때의 원래 경로 (점선)</div>
        <div class="legend-item"><span class="axis-line"></span> 광축</div>
    </div>
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
const lensThickness = document.getElementById("lensThickness");
const radius = document.getElementById("radius");
const prismAngle = document.getElementById("prismAngle");

const lensThicknessRow = document.getElementById("lensThicknessRow");
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
    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 24, 0, Math.PI*2);
    ctx.fillStyle = "#333";
    ctx.fill();
    ctx.strokeStyle = "#111";
    ctx.lineWidth = 3;
    ctx.stroke();

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

    ctx.beginPath();
    ctx.arc(laser.x, laser.y, 7, 0, Math.PI*2);
    ctx.fillStyle = "#ff0000";
    ctx.fill();
}

function drawAxis() {
    drawLine({x: 30, y: axisY}, {x: 1070, y: axisY}, "#aaa", 1, true);
    drawText("광축", 1015, axisY - 10, 13, "#888");
}

/* --- 기구 드로잉 함수들 --- */
function drawConvexLens() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    const th = parseFloat(lensThickness.value);
    ctx.beginPath();
    ctx.moveTo(x - th/2, axisY - h/2);
    ctx.quadraticCurveTo(x + th/2, axisY, x - th/2, axisY + h/2);
    ctx.quadraticCurveTo(x - th*1.5, axisY, x - th/2, axisY - h/2);
    ctx.fillStyle = "rgba(100, 200, 255, 0.35)";
    ctx.fill();
    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;
    ctx.stroke();
}

function drawConcaveLens() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    const th = parseFloat(lensThickness.value);
    ctx.beginPath();
    ctx.moveTo(x - th*1.2, axisY - h/2);
    ctx.lineTo(x + th*0.3, axisY - h/2);
    ctx.quadraticCurveTo(x - th*0.5, axisY, x + th*0.3, axisY + h/2);
    ctx.lineTo(x - th*1.2, axisY + h/2);
    ctx.quadraticCurveTo(x - th*0.5, axisY, x - th*1.2, axisY - h/2);
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

function getConcaveMirrorSpecs() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    const R = parseFloat(radius.value);
    const cx = x - R;
    const sinVal = Math.min(1, h / (2 * R));
    const halfAngle = Math.asin(sinVal);
    return { cx, cy: axisY, R, startAngle: -halfAngle, endAngle: halfAngle, surfaceX: x };
}

function getConvexMirrorSpecs() {
    const x = objectXPos;
    const h = parseFloat(deviceSize.value);
    const R = parseFloat(radius.value);
    const cx = x + R;
    const sinVal = Math.min(1, h / (2 * R));
    const halfAngle = Math.asin(sinVal);
    return { cx, cy: axisY, R, startAngle: Math.PI - halfAngle, endAngle: Math.PI + halfAngle, surfaceX: x };
}

function drawConcaveMirror() {
    const specs = getConcaveMirrorSpecs();
    ctx.beginPath();
    ctx.arc(specs.cx, specs.cy, specs.R, specs.startAngle, specs.endAngle);
    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;
    ctx.stroke();
}

function drawConvexMirror() {
    const specs = getConvexMirrorSpecs();
    ctx.beginPath();
    ctx.arc(specs.cx, specs.cy, specs.R, specs.startAngle, specs.endAngle);
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

function rayCircleIntersectionStrict(p, d, specs) {
    const L = sub(p, { x: specs.cx, y: specs.cy });
    const A = 1;
    const B = 2 * dot(L, d);
    const C = dot(L, L) - specs.R * specs.R;
    const disc = B * B - 4 * A * C;
    if (disc < 0) return null;
    
    const t1 = (-B - Math.sqrt(disc)) / (2 * A);
    const t2 = (-B + Math.sqrt(disc)) / (2 * A);
    let ts = [t1, t2].filter(t => t > 0);
    if (ts.length === 0) return null;
    ts.sort((a,b) => a - b);

    for (let t of ts) {
        const hit = add(p, mul(d, t));
        const angle = Math.atan2(hit.y - specs.cy, hit.x - specs.cx);
        let normalizedAngle = angle;
        if (specs.startAngle < 0 && normalizedAngle > Math.PI) normalizedAngle -= 2 * Math.PI;
        
        if (normalizedAngle >= specs.startAngle - 0.02 && normalizedAngle <= specs.endAngle + 0.02) {
            return { t, point: hit };
        }
    }
    return null;
}

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
        return { ray: { x: incident.x - 2 * dot(incident, n) * n.x, y: incident.y - 2 * dot(incident, n) * n.y }, tir: true };
    }
    const rx = eta * incident.x + (eta * cosi - Math.sqrt(k)) * n.x;
    const ry = eta * incident.y + (eta * cosi - Math.sqrt(k)) * n.y;
    return { ray: normalize({ x: rx, y: ry }), tir: false };
}

/* --- 엄격하고 정밀한 광선 추적 물리 연산 --- */
function traceRays() {
    const type = objectType.value;
    const ox = objectXPos;
    const p = { x: laser.x, y: laser.y };
    const d = normalize({ x: Math.cos(laser.angle), y: Math.sin(laser.angle) });
    const hLimit = parseFloat(deviceSize.value) / 2;
    const th = parseFloat(lensThickness.value);

    if (Math.abs(d.x) < 1e-5) {
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
        return;
    }

    // 직진했을 때의 원래 경로 점선 (배경)
    drawLine(p, add(p, mul(d, 1000)), "#ff9800", 2, true);

    if (type === "convexLens") {
        const frontX = ox - th/2;
        const t = (frontX - p.x) / d.x;
        if (t > 0) {
            const hitIn = add(p, mul(d, t));
            if (Math.abs(hitIn.y - axisY) <= hLimit) {
                drawLine(p, hitIn, "#e53935", 4);

                const yRatio = (hitIn.y - axisY) / hLimit;
                const normal1 = normalize({ x: -1, y: -yRatio * 0.8 });
                const ref1 = refract(d, normal1, 1.0, 1.5);
                const internalRay = ref1.ray;

                const backX = ox + th/2;
                const tBack = (backX - hitIn.x) / internalRay.x;
                if (tBack > 0) {
                    const hitOut = add(hitIn, mul(internalRay, tBack));
                    drawLine(hitIn, hitOut, "#e53935", 4);

                    const outYRatio = (hitOut.y - axisY) / hLimit;
                    const normal2 = normalize({ x: 1, y: outYRatio * 0.8 });
                    const ref2 = refract(internalRay, normal2, 1.5, 1.0);
                    const finalRay = ref2.ray;

                    drawLine(hitOut, add(hitOut, mul(finalRay, 800)), "#e53935", 4);
                    return;
                }
            }
        }
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
    }
    else if (type === "concaveLens") {
        const frontX = ox - th;
        const t = (frontX - p.x) / d.x;
        if (t > 0) {
            const hitIn = add(p, mul(d, t));
            if (Math.abs(hitIn.y - axisY) <= hLimit) {
                drawLine(p, hitIn, "#e53935", 4);

                const yRatio = (hitIn.y - axisY) / hLimit;
                const normal1 = normalize({ x: 1, y: yRatio * 0.8 });
                const ref1 = refract(d, normal1, 1.0, 1.5);
                const internalRay = ref1.ray;

                const backX = ox;
                const tBack = (backX - hitIn.x) / internalRay.x;
                if (tBack > 0) {
                    const hitOut = add(hitIn, mul(internalRay, tBack));
                    drawLine(hitIn, hitOut, "#e53935", 4);

                    const outYRatio = (hitOut.y - axisY) / hLimit;
                    const normal2 = normalize({ x: -1, y: -outYRatio * 0.8 });
                    const ref2 = refract(internalRay, normal2, 1.5, 1.0);
                    const finalRay = ref2.ray;

                    drawLine(hitOut, add(hitOut, mul(finalRay, 800)), "#e53935", 4);
                    return;
                }
            }
        }
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
    }
    else if (type === "planeMirror") {
        const t = (ox - p.x) / d.x;
        const hitPoint = add(p, mul(d, t));
        if (t > 0 && Math.abs(hitPoint.y - axisY) <= hLimit) {
            drawLine(p, hitPoint, "#e53935", 4);
            const n = { x: -1, y: 0 };
            const dotND = dot(d, n);
            const outDir = { x: d.x - 2 * dotND * n.x, y: d.y - 2 * dotND * n.y };
            drawLine(hitPoint, add(hitPoint, mul(outDir, 800)), "#e53935", 4);
            return;
        }
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
    }
    else if (type === "concaveMirror") {
        const specs = getConcaveMirrorSpecs();
        const hitResult = rayCircleIntersectionStrict(p, d, specs);
        if (hitResult !== null) {
            const actualHit = hitResult.point;
            drawLine(p, actualHit, "#e53935", 4);
            const normal = normalize(sub(actualHit, { x: specs.cx, y: specs.cy }));
            const dotND = dot(d, normal);
            const outDir = { x: d.x - 2 * dotND * normal.x, y: d.y - 2 * dotND * normal.y };
            drawLine(actualHit, add(actualHit, mul(outDir, 800)), "#e53935", 4);
            return;
        }
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
    }
    else if (type === "convexMirror") {
        const specs = getConvexMirrorSpecs();
        const hitResult = rayCircleIntersectionStrict(p, d, specs);
        if (hitResult !== null) {
            const actualHit = hitResult.point;
            drawLine(p, actualHit, "#e53935", 4);
            const normal = normalize(sub({ x: specs.cx, y: specs.cy }, actualHit));
            const dotND = dot(d, normal);
            const outDir = { x: d.x - 2 * dotND * normal.x, y: d.y - 2 * dotND * normal.y };
            drawLine(actualHit, add(actualHit, mul(outDir, 800)), "#e53935", 4);
            return;
        }
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
    }
    else if (type === "prism") {
        const A = parseFloat(prismAngle.value) * Math.PI / 180;
        const base = parseFloat(deviceSize.value);
        const height = base / (2 * Math.tan(A / 2));
        
        const Vbl = { x: ox - base / 2, y: axisY + height / 2 };
        const Vtop = { x: ox, y: axisY - height / 2 };
        const Vbr = { x: ox + base / 2, y: axisY + height / 2 };

        const edges = [
            { a: Vbl, b: Vtop },
            { a: Vtop, b: Vbr },
            { a: Vbl, b: Vbr }
        ];

        let firstHit = null;
        let matchedEdge = null;

        for (let edge of edges) {
            const inter = getSegmentIntersection(p, d, edge.a, edge.b);
            if (inter) {
                if (!firstHit || inter.t < firstHit.t) {
                    firstHit = inter;
                    matchedEdge = edge;
                }
            }
        }

        if (firstHit && matchedEdge) {
            drawLine(p, firstHit.point, "#e53935", 4);
            
            const vFace1 = sub(matchedEdge.b, matchedEdge.a);
            let normal1 = normalize({ x: -vFace1.y, y: vFace1.x });
            if (dot(d, normal1) > 0) normal1 = { x: -normal1.x, y: -normal1.y };

            const ref1 = refract(d, normal1, 1.0, 1.5);
            const rRay1 = ref1.ray;

            let secondHit = null;
            let secondFace = null;
            for (let edge of edges) {
                if (edge === matchedEdge) continue;
                const inter2 = getSegmentIntersection(firstHit.point, rRay1, edge.a, edge.b);
                if (inter2) {
                    // 내부에서 지나가는 교차점 중 첫 번째 유효 출사점 찾기
                    if (!secondHit || inter2.t < secondHit.t) {
                        secondHit = inter2;
                        secondFace = edge;
                    }
                }
            }

            if (secondHit && secondFace) {
                drawLine(firstHit.point, secondHit.point, "#e53935", 4);

                const vFace2 = sub(secondFace.b, secondFace.a);
                let normal2 = normalize({ x: vFace2.y, y: -vFace2.x });
                if (dot(rRay1, normal2) > 0) normal2 = { x: -normal2.x, y: -normal2.y };

                const ref2 = refract(rRay1, normal2, 1.5, 1.0);
                const rRay2 = ref2.ray;

                drawLine(secondHit.point, add(secondHit.point, mul(rRay2, 800)), "#e53935", 4);
                return;
            }
        }
        drawLine(p, add(p, mul(d, 1000)), "#e53935", 4);
    }
}

function updateVisibility() {
    const type = objectType.value;
    const isLens = (type === "convexLens" || type === "concaveLens");
    lensThicknessRow.style.display = isLens ? "grid" : "none";
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
}

/* --- 마우스 인터랙션 --- */
canvas.addEventListener("mousedown", (e) => {
    const mouse = getCanvasMousePos(e);

    const lHandle = laserHandlePos();
    if (Math.hypot(mouse.x - lHandle.x, mouse.y - lHandle.y) < 25) {
        draggingLaserHandle = true;
        return;
    }

    const hLimit = parseFloat(deviceSize.value) / 2;
    if (mouse.x >= objectXPos - 70 && mouse.x <= objectXPos + 70 && mouse.y >= axisY - hLimit - 30 && mouse.y <= axisY + hLimit + 30) {
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

objectType.addEventListener("change", () => { updateVisibility(); render(); });
deviceSize.addEventListener("input", () => { document.getElementById("deviceSizeValue").innerText = deviceSize.value; render(); });
lensThickness.addEventListener("input", () => { document.getElementById("lensThicknessValue").innerText = lensThickness.value; render(); });
radius.addEventListener("input", () => { document.getElementById("radiusValue").innerText = radius.value; render(); });
prismAngle.addEventListener("input", () => { document.getElementById("prismAngleValue").innerText = prismAngle.value + "°"; render(); });

updateVisibility();
render();
</script>
</body>
</html>
"""

components.html(html_code, height=920, scrolling=True)
