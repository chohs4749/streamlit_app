import streamlit as str_module
import streamlit.components.v1 as components

str_module.set_page_config(
    page_title="렌즈,거울,프리즘 실험해보기",
    layout="wide"
)

str_module.title(" 렌즈,거울,프리즘 실험해보기 ")

str_module.markdown(
    """
    - **노란색 손잡이 (레이저)**: 드래그하여 레이저의 발사 방향 조절 가능.
    - **광학 기구 직접 드래그**: 렌즈, 거울, 프리즘 기구를 마우스로 직접 클릭하여 좌우로 이동 가능.
    - **점선**: 레이저가 굴절이나 반사를 받지 않고 직진했을 때의 원래 레이저 경로.
    """
)

html_code = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

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

.real-line {
    width: 40px;
    border-top: 4px solid #e53935;
}

.virtual-line {
    width: 40px;
    border-top: 2px dashed #ff9800;
}

.axis-line {
    width: 40px;
    border-top: 2px dashed #aaa;
}
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

        <input
            id="deviceSize"
            type="range"
            min="120"
            max="360"
            value="220"
        >

        <span id="deviceSizeValue" class="value">220</span>

    </div>


    <div id="lensThicknessRow" class="control-grid">

        <label>렌즈 두께</label>

        <input
            id="lensThickness"
            type="range"
            min="20"
            max="70"
            value="40"
        >

        <span id="lensThicknessValue" class="value">40</span>

    </div>


    <div id="radiusRow"
         class="control-grid"
         style="display:none;">

        <label>거울 곡률반지름 (R)</label>

        <input
            id="radius"
            type="range"
            min="100"
            max="350"
            value="220"
        >

        <span id="radiusValue" class="value">220</span>

    </div>


    <div id="prismRow"
         class="control-grid"
         style="display:none;">

        <label>프리즘 꼭짓각</label>

        <input
            id="prismAngle"
            type="range"
            min="30"
            max="80"
            value="60"
        >

        <span id="prismAngleValue" class="value">60°</span>

    </div>

</div>


<div class="panel">

    <canvas
        id="canvas"
        width="1100"
        height="680"
    ></canvas>

    <div class="legend">

        <div class="legend-item">
            <span class="real-line"></span>
            실제 레이저 광선 (굴절/반사)
        </div>

        <div class="legend-item">
            <span class="virtual-line"></span>
            직진했을 때의 원래 경로 (점선)
        </div>

        <div class="legend-item">
            <span class="axis-line"></span>
            광축
        </div>

    </div>

</div>


<script>

const canvas =
    document.getElementById("canvas");

const ctx =
    canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

const axisY = H / 2;


const laser = {
    x: 90,
    y: axisY,
    angle: 0
};


let objectXPos = 650;

let draggingLaserHandle = false;
let draggingDevice = false;


const objectType =
    document.getElementById("objectType");

const deviceSize =
    document.getElementById("deviceSize");

const lensThickness =
    document.getElementById("lensThickness");

const radius =
    document.getElementById("radius");

const prismAngle =
    document.getElementById("prismAngle");

const lensThicknessRow =
    document.getElementById("lensThicknessRow");

const radiusRow =
    document.getElementById("radiusRow");

const prismRow =
    document.getElementById("prismRow");


function add(a,b) {

    return {
        x:a.x+b.x,
        y:a.y+b.y
    };

}


function sub(a,b) {

    return {
        x:a.x-b.x,
        y:a.y-b.y
    };

}


function mul(a,k) {

    return {
        x:a.x*k,
        y:a.y*k
    };

}


function length(a) {

    return Math.sqrt(
        a.x*a.x +
        a.y*a.y
    );

}


function normalize(a) {

    const l = length(a);

    if(l === 0) {

        return {
            x:1,
            y:0
        };

    }

    return {
        x:a.x/l,
        y:a.y/l
    };

}


function dot(a,b) {

    return (
        a.x*b.x +
        a.y*b.y
    );

}


function cross(a,b) {

    return (
        a.x*b.y -
        a.y*b.x
    );

}


function drawLine(
    p1,
    p2,
    color="#e53935",
    width=4,
    dashed=false
) {

    ctx.beginPath();

    ctx.setLineDash(
        dashed
        ? [10,8]
        : []
    );

    ctx.moveTo(
        p1.x,
        p1.y
    );

    ctx.lineTo(
        p2.x,
        p2.y
    );

    ctx.strokeStyle = color;
    ctx.lineWidth = width;

    ctx.stroke();

    ctx.setLineDash([]);

}


function drawText(
    value,
    x,
    y,
    size=15,
    color="#222"
) {

    ctx.fillStyle = color;

    ctx.font =
        "bold " +
        size +
        "px Arial";

    ctx.fillText(
        value,
        x,
        y
    );

}


function laserHandlePos() {

    return {

        x:
            laser.x +
            Math.cos(laser.angle)*75,

        y:
            laser.y +
            Math.sin(laser.angle)*75

    };

}


function getCanvasMousePos(e) {

    const rect =
        canvas.getBoundingClientRect();

    const scaleX =
        canvas.width /
        rect.width;

    const scaleY =
        canvas.height /
        rect.height;

    return {

        x:
            (e.clientX -
             rect.left) *
            scaleX,

        y:
            (e.clientY -
             rect.top) *
            scaleY

    };

}


function drawLaserAndHandle() {

    ctx.beginPath();

    ctx.arc(
        laser.x,
        laser.y,
        24,
        0,
        Math.PI*2
    );

    ctx.fillStyle = "#333";

    ctx.fill();

    ctx.strokeStyle = "#111";
    ctx.lineWidth = 3;

    ctx.stroke();


    const lHandle =
        laserHandlePos();


    drawLine(
        {
            x:laser.x,
            y:laser.y
        },
        lHandle,
        "#fbc02d",
        12
    );


    ctx.beginPath();

    ctx.arc(
        lHandle.x,
        lHandle.y,
        14,
        0,
        Math.PI*2
    );

    ctx.fillStyle = "#ffdf3f";

    ctx.fill();

    ctx.strokeStyle = "#806000";
    ctx.lineWidth = 2;

    ctx.stroke();


    drawText(
        "레이저",
        lHandle.x-22,
        lHandle.y-20,
        11,
        "#555"
    );


    ctx.beginPath();

    ctx.arc(
        laser.x,
        laser.y,
        7,
        0,
        Math.PI*2
    );

    ctx.fillStyle = "#ff0000";

    ctx.fill();

}


function drawAxis() {

    drawLine(
        {
            x:30,
            y:axisY
        },
        {
            x:1070,
            y:axisY
        },
        "#aaa",
        1,
        true
    );

    drawText(
        "광축",
        1015,
        axisY-10,
        13,
        "#888"
    );

}


/* =========================================================
   렌즈 모양
   ========================================================= */

function getLensGeometry() {

    const x =
        objectXPos;

    const h =
        parseFloat(
            deviceSize.value
        );

    const th =
        parseFloat(
            lensThickness.value
        );

    const R =
        (
            (h/2)*(h/2) +
            (th/2)*(th/2)
        ) / th;

    return {
        x,
        h,
        th,
        R
    };

}


function drawConvexLens() {

    const g =
        getLensGeometry();

    ctx.beginPath();

    ctx.moveTo(
        g.x-g.th/2,
        axisY-g.h/2
    );

    ctx.quadraticCurveTo(
        g.x+g.th/2,
        axisY,
        g.x-g.th/2,
        axisY+g.h/2
    );

    ctx.quadraticCurveTo(
        g.x-g.th*1.5,
        axisY,
        g.x-g.th/2,
        axisY-g.h/2
    );

    ctx.fillStyle =
        "rgba(100,200,255,0.35)";

    ctx.fill();

    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;

    ctx.stroke();

}


function drawConcaveLens() {

    const g =
        getLensGeometry();

    ctx.beginPath();

    ctx.moveTo(
        g.x-g.th*1.2,
        axisY-g.h/2
    );

    ctx.lineTo(
        g.x+g.th*0.3,
        axisY-g.h/2
    );

    ctx.quadraticCurveTo(
        g.x-g.th*0.5,
        axisY,
        g.x+g.th*0.3,
        axisY+g.h/2
    );

    ctx.lineTo(
        g.x-g.th*1.2,
        axisY+g.h/2
    );

    ctx.quadraticCurveTo(
        g.x-g.th*0.5,
        axisY,
        g.x-g.th*1.2,
        axisY-g.h/2
    );

    ctx.fillStyle =
        "rgba(100,200,255,0.35)";

    ctx.fill();

    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 3;

    ctx.stroke();

}


/* =========================================================
   렌즈의 실제 곡면 정보

   화면에 그려지는 곡선과
   광선이 실제로 만나는 위치를 동일하게 사용한다.
   ========================================================= */

function getLensSurfaces(type) {

    const g =
        getLensGeometry();

    let front;
    let back;

    if(type === "convexLens") {

        /*
         * 왼쪽 곡면 = 입사면
         */
        front = {
            p0:{
                x:g.x-g.th/2,
                y:axisY-g.h/2
            },

            p1:{
                x:g.x+g.th/2,
                y:axisY
            },

            p2:{
                x:g.x-g.th/2,
                y:axisY+g.h/2
            }
        };

        /*
         * 오른쪽 곡면 = 출사면
         */
        back = {
            p0:{
                x:g.x-g.th/2,
                y:axisY+g.h/2
            },

            p1:{
                x:g.x-g.th*1.5,
                y:axisY
            },

            p2:{
                x:g.x-g.th/2,
                y:axisY-g.h/2
            }
        };

    }

    else {

        /*
         * 오목렌즈 왼쪽 곡면 = 입사면
         */
        front = {
            p0:{
                x:g.x-g.th*1.2,
                y:axisY+g.h/2
            },

            p1:{
                x:g.x-g.th*0.5,
                y:axisY
            },

            p2:{
                x:g.x-g.th*1.2,
                y:axisY-g.h/2
            }
        };

        /*
         * 오목렌즈 오른쪽 곡면 = 출사면
         */
        back = {
            p0:{
                x:g.x+g.th*0.3,
                y:axisY-g.h/2
            },

            p1:{
                x:g.x-g.th*0.5,
                y:axisY
            },

            p2:{
                x:g.x+g.th*0.3,
                y:axisY+g.h/2
            }
        };

    }

    return {
        front,
        back
    };

}


/* 베지어 곡선 위의 점 */
function quadraticPoint(curve,u) {

    const v = 1-u;

    return {

        x:
            v*v*curve.p0.x +
            2*v*u*curve.p1.x +
            u*u*curve.p2.x,

        y:
            v*v*curve.p0.y +
            2*v*u*curve.p1.y +
            u*u*curve.p2.y

    };

}


/*
 * 레이저와 2차 베지어 곡선의 교점
 */
function quadraticRayIntersection(
    p,
    d,
    curve
) {

    const A =
        sub(
            add(
                curve.p0,
                curve.p2
            ),
            mul(
                curve.p1,
                2
            )
        );

    const B =
        mul(
            sub(
                curve.p1,
                curve.p0
            ),
            2
        );

    const C =
        sub(
            curve.p0,
            p
        );


    const qa =
        cross(A,d);

    const qb =
        cross(B,d);

    const qc =
        cross(C,d);


    let roots = [];


    if(Math.abs(qa) < 1e-9) {

        if(Math.abs(qb) < 1e-9) {

            return null;

        }

        roots.push(
            -qc/qb
        );

    }

    else {

        const discriminant =
            qb*qb -
            4*qa*qc;

        if(discriminant < 0) {

            return null;

        }

        const sqrtD =
            Math.sqrt(discriminant);

        roots.push(
            (-qb-sqrtD)/(2*qa)
        );

        roots.push(
            (-qb+sqrtD)/(2*qa)
        );

    }


    const candidates = [];


    for(const u of roots) {

        if(
            u < -1e-7 ||
            u > 1+1e-7
        ) {

            continue;

        }

        const uu =
            Math.max(
                0,
                Math.min(
                    1,
                    u
                )
            );

        const hit =
            quadraticPoint(
                curve,
                uu
            );

        const t =
            dot(
                sub(hit,p),
                d
            );

        if(t > 1e-4) {

            candidates.push({
                t:t,
                u:uu,
                point:hit
            });

        }

    }


    if(candidates.length === 0) {

        return null;

    }


    candidates.sort(
        (a,b) =>
            a.t-b.t
    );


    return candidates[0];

}


/*
 * 곡선의 접선
 */
function quadraticTangent(curve,u) {

    return normalize({

        x:
            2 *
            (
                (1-u) *
                (curve.p1.x-curve.p0.x)
                +
                u *
                (curve.p2.x-curve.p1.x)
            ),

        y:
            2 *
            (
                (1-u) *
                (curve.p1.y-curve.p0.y)
                +
                u *
                (curve.p2.y-curve.p1.y)
            )

    });

}


/*
 * 곡면의 바깥쪽 법선
 *
 * insidePoint는 렌즈 내부에 있는 점이다.
 */
function getLensNormal(
    curve,
    u,
    hitPoint,
    insidePoint
) {

    const tangent =
        quadraticTangent(
            curve,
            u
        );

    let normal = {
        x:-tangent.y,
        y:tangent.x
    };


    /*
     * 법선이 렌즈 내부를 향하면 반전
     */
    if(
        dot(
            normal,
            sub(
                insidePoint,
                hitPoint
            )
        ) > 0
    ) {

        normal = {
            x:-normal.x,
            y:-normal.y
        };

    }


    return normalize(normal);

}


/* =========================================================
   스넬의 법칙
   ========================================================= */

function refract(I,N,n1,n2) {

    I = normalize(I);
    N = normalize(N);

    let cosI =
        -dot(I,N);


    if(cosI < 0) {

        N = {
            x:-N.x,
            y:-N.y
        };

        cosI =
            -dot(I,N);

    }


    cosI =
        Math.max(
            0,
            Math.min(
                1,
                cosI
            )
        );


    const eta =
        n1/n2;


    const sin2T =
        eta*eta *
        (
            1 -
            cosI*cosI
        );


    if(sin2T > 1) {

        return {
            ray:null,
            totalInternalReflection:true
        };

    }


    const cosT =
        Math.sqrt(
            Math.max(
                0,
                1-sin2T
            )
        );


    const T = {

        x:
            eta*I.x +
            (
                eta*cosI-cosT
            )*N.x,

        y:
            eta*I.y +
            (
                eta*cosI-cosT
            )*N.y

    };


    return {
        ray:normalize(T),
        totalInternalReflection:false
    };

}


function reflectRay(I,N) {

    I = normalize(I);
    N = normalize(N);

    const k =
        dot(I,N);

    return normalize({

        x:
            I.x -
            2*k*N.x,

        y:
            I.y -
            2*k*N.y

    });

}


/* =========================================================
   거울 / 프리즘 관련 기존 함수
   ========================================================= */

function getSegmentIntersection(
    p,
    d,
    a,
    b
) {

    const v =
        sub(b,a);

    const crossValue =
        d.x*(-v.y) -
        d.y*(-v.x);

    if(
        Math.abs(crossValue)<1e-6
    )
        return null;

    const ap =
        sub(a,p);

    const t =
        (
            ap.x*(-v.y) -
            ap.y*(-v.x)
        ) /
        crossValue;

    const s =
        (
            d.x*ap.y -
            d.y*ap.x
        ) /
        crossValue;

    if(
        t>1e-4 &&
        s>=0 &&
        s<=1
    ) {

        return {

            t,
            s,

            point:
                add(
                    p,
                    mul(d,t)
                )

        };

    }

    return null;

}


function rayCircleIntersectionStrict(
    p,
    d,
    specs
) {

    const L =
        sub(
            p,
            {
                x:specs.cx,
                y:specs.cy
            }
        );

    const B =
        2*dot(L,d);

    const C =
        dot(L,L) -
        specs.R*specs.R;

    const disc =
        B*B -
        4*C;

    if(disc<0)
        return null;

    const sqrtDisc =
        Math.sqrt(disc);

    const t1 =
        (-B-sqrtDisc)/2;

    const t2 =
        (-B+sqrtDisc)/2;

    let ts =
        [t1,t2]
        .filter(
            t=>t>1e-4
        );

    if(ts.length===0)
        return null;

    ts.sort(
        (a,b)=>a-b
    );


    for(const t of ts) {

        const hit =
            add(
                p,
                mul(d,t)
            );

        const angle =
            Math.atan2(
                hit.y-specs.cy,
                hit.x-specs.cx
            );

        let sa =
            specs.startAngle;

        let ea =
            specs.endAngle;

        let ang =
            angle;


        if(ang<0)
            ang += Math.PI*2;

        if(sa<0)
            sa += Math.PI*2;

        if(ea<0)
            ea += Math.PI*2;


        if(sa>ea) {

            if(
                ang>=sa ||
                ang<=ea
            ) {

                return {
                    t,
                    point:hit
                };

            }

        }

        else {

            if(
                ang>=sa &&
                ang<=ea
            ) {

                return {
                    t,
                    point:hit
                };

            }

        }

    }

    return null;

}


function getOutwardNormal(edge,center) {

    const face =
        sub(
            edge.b,
            edge.a
        );

    let n =
        normalize({
            x:-face.y,
            y:face.x
        });


    const midpoint = {

        x:
            (edge.a.x+edge.b.x)/2,

        y:
            (edge.a.y+edge.b.y)/2

    };


    const towardCenter =
        sub(
            center,
            midpoint
        );


    if(
        dot(
            n,
            towardCenter
        ) > 0
    ) {

        n = {
            x:-n.x,
            y:-n.y
        };

    }


    return n;

}


/* =========================================================
   거울 모양
   ========================================================= */

function drawPlaneMirror() {

    const x =
        objectXPos;

    const h =
        parseFloat(
            deviceSize.value
        );

    drawLine(
        {
            x:x,
            y:axisY-h/2
        },
        {
            x:x,
            y:axisY+h/2
        },
        "#37474f",
        5
    );


    for(
        let y=axisY-h/2+10;
        y<axisY+h/2;
        y+=15
    ) {

        drawLine(
            {
                x:x,
                y:y
            },
            {
                x:x+10,
                y:y+10
            },
            "#78909c",
            2
        );

    }

}


function getConcaveMirrorSpecs() {

    const x =
        objectXPos;

    const h =
        parseFloat(
            deviceSize.value
        );

    const R =
        parseFloat(
            radius.value
        );

    const cx =
        x-R;

    const sinVal =
        Math.min(
            1,
            h/(2*R)
        );

    const halfAngle =
        Math.asin(sinVal);

    return {

        cx,
        cy:axisY,
        R,

        startAngle:
            -halfAngle,

        endAngle:
            halfAngle,

        surfaceX:x

    };

}


function getConvexMirrorSpecs() {

    const x =
        objectXPos;

    const h =
        parseFloat(
            deviceSize.value
        );

    const R =
        parseFloat(
            radius.value
        );

    const cx =
        x+R;

    const sinVal =
        Math.min(
            1,
            h/(2*R)
        );

    const halfAngle =
        Math.asin(sinVal);

    return {

        cx,
        cy:axisY,
        R,

        startAngle:
            Math.PI-halfAngle,

        endAngle:
            Math.PI+halfAngle,

        surfaceX:x

    };

}


function drawConcaveMirror() {

    const specs =
        getConcaveMirrorSpecs();

    ctx.beginPath();

    ctx.arc(
        specs.cx,
        specs.cy,
        specs.R,
        specs.startAngle,
        specs.endAngle
    );

    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;

    ctx.stroke();

}


function drawConvexMirror() {

    const specs =
        getConvexMirrorSpecs();

    ctx.beginPath();

    ctx.arc(
        specs.cx,
        specs.cy,
        specs.R,
        specs.startAngle,
        specs.endAngle
    );

    ctx.strokeStyle = "#37474f";
    ctx.lineWidth = 5;

    ctx.stroke();

}


function drawPrism() {

    const x =
        objectXPos;

    const A =
        parseFloat(
            prismAngle.value
        ) *
        Math.PI/180;

    const base =
        parseFloat(
            deviceSize.value
        );

    const height =
        base /
        (
            2*Math.tan(A/2)
        );


    ctx.beginPath();

    ctx.moveTo(
        x-base/2,
        axisY+height/2
    );

    ctx.lineTo(
        x,
        axisY-height/2
    );

    ctx.lineTo(
        x+base/2,
        axisY+height/2
    );

    ctx.closePath();


    ctx.fillStyle =
        "rgba(100,200,255,0.3)";

    ctx.fill();

    ctx.strokeStyle = "#0288d1";
    ctx.lineWidth = 4;

    ctx.stroke();

}


/* =========================================================
   광선 추적
   ========================================================= */

function traceRays() {

    const type =
        objectType.value;


    const ox =
        objectXPos;


    const p = {

        x:laser.x,
        y:laser.y

    };


    const d =
        normalize({

            x:
                Math.cos(
                    laser.angle
                ),

            y:
                Math.sin(
                    laser.angle
                )

        });


    const hLimit =
        parseFloat(
            deviceSize.value
        )/2;


    /* =====================================================
       볼록렌즈
       ===================================================== */

    if(type==="convexLens") {

        const surfaces =
            getLensSurfaces(
                "convexLens"
            );


        const frontHit =
            quadraticRayIntersection(
                p,
                d,
                surfaces.front
            );


        const backHit =
            frontHit
            ? quadraticRayIntersection(
                frontHit.point,
                d,
                surfaces.back
            )
            : null;


        /*
         * 렌즈에 닿지 않으면
         * 실제 광선과 점선을 모두 직진
         */
        if(
            !frontHit ||
            !backHit
        ) {

            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#e53935",
                4
            );

            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#ff9800",
                2,
                true
            );

            return;

        }


        /*
         * 렌즈 내부의 기준점
         */
        const frontMiddle =
            quadraticPoint(
                surfaces.front,
                0.5
            );

        const backMiddle =
            quadraticPoint(
                surfaces.back,
                0.5
            );

        const insidePoint = {

            x:
                (
                    frontMiddle.x +
                    backMiddle.x
                )/2,

            y:
                (
                    frontMiddle.y +
                    backMiddle.y
                )/2

        };


        /*
         * 첫 번째 굴절
         * 공기 → 렌즈
         */
        const normalIn =
            getLensNormal(
                surfaces.front,
                frontHit.u,
                frontHit.point,
                insidePoint
            );


        const refractedIn =
            refract(
                d,
                normalIn,
                1.0,
                1.5
            );


        /*
         * 원래 직진 경로 점선
         */
        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#ff9800",
            2,
            true
        );


        /*
         * 입사 전 광선
         */
        drawLine(
            p,
            frontHit.point,
            "#e53935",
            4
        );


        if(
            !refractedIn.ray
        ) {

            return;

        }


        /*
         * 렌즈 내부 광선
         */
        const insideDir =
            refractedIn.ray;


        /*
         * 두 번째 굴절
         * 렌즈 → 공기
         */
        const normalOut =
            getLensNormal(
                surfaces.back,
                backHit.u,
                backHit.point,
                insidePoint
            );


        const refractedOut =
            refract(
                insideDir,
                normalOut,
                1.5,
                1.0
            );


        /*
         * 첫 번째 굴절점부터
         * 두 번째 굴절점까지는
         * 렌즈 내부에서 직선
         */
        drawLine(
            frontHit.point,
            backHit.point,
            "#e53935",
            4
        );


        /*
         * 두 번째 굴절
         */
        if(
            refractedOut.ray
        ) {

            drawLine(
                backHit.point,
                add(
                    backHit.point,
                    mul(
                        refractedOut.ray,
                        800
                    )
                ),
                "#e53935",
                4
            );

        }

        else {

            /*
             * 전반사가 일어나는 경우
             */
            const reflected =
                reflectRay(
                    insideDir,
                    normalOut
                );

            drawLine(
                backHit.point,
                add(
                    backHit.point,
                    mul(
                        reflected,
                        800
                    )
                ),
                "#e53935",
                4
            );

        }

        return;

    }


    /* =====================================================
       오목렌즈
       ===================================================== */

    else if(type==="concaveLens") {

        const surfaces =
            getLensSurfaces(
                "concaveLens"
            );


        /*
         * 첫 번째 면과의 교점
         */
        const frontHit =
            quadraticRayIntersection(
                p,
                d,
                surfaces.front
            );


        /*
         * 첫 번째 굴절 후 방향을 계산하기 전에
         * 실제 렌즈 내부의 기준점을 구한다.
         */
        const frontMiddle =
            quadraticPoint(
                surfaces.front,
                0.5
            );

        const backMiddle =
            quadraticPoint(
                surfaces.back,
                0.5
            );

        const insidePoint = {

            x:
                (
                    frontMiddle.x +
                    backMiddle.x
                )/2,

            y:
                (
                    frontMiddle.y +
                    backMiddle.y
                )/2

        };


        /*
         * 렌즈에 닿지 않는 경우
         */
        if(!frontHit) {

            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#e53935",
                4
            );

            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#ff9800",
                2,
                true
            );

            return;

        }


        /*
         * 첫 번째 면에서의 법선
         */
        const normalIn =
            getLensNormal(
                surfaces.front,
                frontHit.u,
                frontHit.point,
                insidePoint
            );


        /*
         * 공기 → 오목렌즈
         */
        const refractedIn =
            refract(
                d,
                normalIn,
                1.0,
                1.5
            );


        /*
         * 원래 직진 경로
         */
        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#ff9800",
            2,
            true
        );


        /*
         * 입사 전 광선
         */
        drawLine(
            p,
            frontHit.point,
            "#e53935",
            4
        );


        if(
            !refractedIn.ray
        ) {

            return;

        }


        const insideDir =
            refractedIn.ray;


        /*
         * 두 번째 면까지 실제로 진행
         */
        const backHit =
            quadraticRayIntersection(
                frontHit.point,
                insideDir,
                surfaces.back
            );


        /*
         * 두 번째 면을 못 찾으면
         * 렌즈 내부 광선을 그대로 연장
         */
        if(!backHit) {

            drawLine(
                frontHit.point,
                add(
                    frontHit.point,
                    mul(
                        insideDir,
                        800
                    )
                ),
                "#e53935",
                4
            );

            return;

        }


        /*
         * 렌즈 내부에서는 굴절 없이 직선
         */
        drawLine(
            frontHit.point,
            backHit.point,
            "#e53935",
            4
        );


        /*
         * 두 번째 면의 법선
         */
        const normalOut =
            getLensNormal(
                surfaces.back,
                backHit.u,
                backHit.point,
                insidePoint
            );


        /*
         * 렌즈 → 공기
         */
        const refractedOut =
            refract(
                insideDir,
                normalOut,
                1.5,
                1.0
            );


        if(
            refractedOut.ray
        ) {

            /*
             * 최종적으로 발산하는 실제 광선
             */
            drawLine(
                backHit.point,
                add(
                    backHit.point,
                    mul(
                        refractedOut.ray,
                        800
                    )
                ),
                "#e53935",
                4
            );

        }

        else {

            const reflected =
                reflectRay(
                    insideDir,
                    normalOut
                );

            drawLine(
                backHit.point,
                add(
                    backHit.point,
                    mul(
                        reflected,
                        800
                    )
                ),
                "#e53935",
                4
            );

        }

        return;

    }


    /* =====================================================
       평면거울
       ===================================================== */

    else if(type==="planeMirror") {

        const t =
            (ox-p.x)/d.x;


        const hitPoint =
            add(
                p,
                mul(d,t)
            );


        if(
            t>1e-4 &&
            Math.abs(
                hitPoint.y-axisY
            )<=hLimit
        ) {

            drawLine(
                p,
                hitPoint,
                "#e53935",
                4
            );


            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#ff9800",
                2,
                true
            );


            const n = {
                x:-1,
                y:0
            };


            const dotND =
                dot(d,n);


            const outDir = {

                x:
                    d.x -
                    2*dotND*n.x,

                y:
                    d.y -
                    2*dotND*n.y

            };


            drawLine(
                hitPoint,
                add(
                    hitPoint,
                    mul(outDir,800)
                ),
                "#e53935",
                4
            );


            return;

        }


        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            4
        );


        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#ff9800",
            2,
            true
        );


        return;

    }


    /* =====================================================
       오목거울
       ===================================================== */

    else if(type==="concaveMirror") {

        const specs =
            getConcaveMirrorSpecs();


        const hitResult =
            rayCircleIntersectionStrict(
                p,
                d,
                specs
            );


        if(hitResult!==null) {

            const actualHit =
                hitResult.point;


            drawLine(
                p,
                actualHit,
                "#e53935",
                4
            );


            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#ff9800",
                2,
                true
            );


            const normal =
                normalize(
                    sub(
                        actualHit,
                        {
                            x:specs.cx,
                            y:specs.cy
                        }
                    )
                );


            const dotND =
                dot(d,normal);


            const outDir = {

                x:
                    d.x -
                    2*dotND*normal.x,

                y:
                    d.y -
                    2*dotND*normal.y

            };


            drawLine(
                actualHit,
                add(
                    actualHit,
                    mul(outDir,800)
                ),
                "#e53935",
                4
            );


            return;

        }


        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            4
        );


        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#ff9800",
            2,
            true
        );


        return;

    }


    /* =====================================================
       볼록거울
       ===================================================== */

    else if(type==="convexMirror") {

        const specs =
            getConvexMirrorSpecs();


        const hitResult =
            rayCircleIntersectionStrict(
                p,
                d,
                specs
            );


        if(hitResult!==null) {

            const actualHit =
                hitResult.point;


            drawLine(
                p,
                actualHit,
                "#e53935",
                4
            );


            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#ff9800",
                2,
                true
            );


            const normal =
                normalize(
                    sub(
                        {
                            x:specs.cx,
                            y:specs.cy
                        },
                        actualHit
                    )
                );


            const dotND =
                dot(d,normal);


            const outDir = {

                x:
                    d.x -
                    2*dotND*normal.x,

                y:
                    d.y -
                    2*dotND*normal.y

            };


            drawLine(
                actualHit,
                add(
                    actualHit,
                    mul(outDir,800)
                ),
                "#e53935",
                4
            );


            return;

        }


        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            4
        );


        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#ff9800",
            2,
            true
        );


        return;

    }


    /* =====================================================
       프리즘
       ===================================================== */

    else if(type==="prism") {

        const A =
            parseFloat(
                prismAngle.value
            ) *
            Math.PI/180;


        const base =
            parseFloat(
                deviceSize.value
            );


        const height =
            base /
            (
                2*Math.tan(A/2)
            );


        const Vbl = {

            x:
                ox-base/2,

            y:
                axisY+height/2

        };


        const Vtop = {

            x:ox,
            y:axisY-height/2

        };


        const Vbr = {

            x:
                ox+base/2,

            y:
                axisY+height/2

        };


        const edges = [

            {
                a:Vbl,
                b:Vtop
            },

            {
                a:Vtop,
                b:Vbr
            },

            {
                a:Vbl,
                b:Vbr
            }

        ];


        const prismCenter = {

            x:
                (
                    Vbl.x +
                    Vtop.x +
                    Vbr.x
                )/3,

            y:
                (
                    Vbl.y +
                    Vtop.y +
                    Vbr.y
                )/3

        };


        let firstHit = null;
        let firstFace = null;


        for(const edge of edges) {

            const inter =
                getSegmentIntersection(
                    p,
                    d,
                    edge.a,
                    edge.b
                );


            if(inter) {

                if(
                    !firstHit ||
                    inter.t < firstHit.t
                ) {

                    firstHit = inter;
                    firstFace = edge;

                }

            }

        }


        if(
            !firstHit ||
            !firstFace
        ) {

            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#e53935",
                4
            );


            drawLine(
                p,
                add(
                    p,
                    mul(d,1000)
                ),
                "#ff9800",
                2,
                true
            );


            return;

        }


        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#ff9800",
            2,
            true
        );


        drawLine(
            p,
            firstHit.point,
            "#e53935",
            4
        );


        const normalIn =
            getOutwardNormal(
                firstFace,
                prismCenter
            );


        const firstRefraction =
            refract(
                d,
                normalIn,
                1.0,
                1.5
            );


        if(
            firstRefraction.totalInternalReflection ||
            !firstRefraction.ray
        ) {

            const reflected =
                reflectRay(
                    d,
                    normalIn
                );


            drawLine(
                firstHit.point,
                add(
                    firstHit.point,
                    mul(reflected,800)
                ),
                "#e53935",
                4
            );


            return;

        }


        let currentPoint =
            firstHit.point;

        let currentDir =
            firstRefraction.ray;

        let currentMedium =
            1.5;


        for(
            let bounce=0;
            bounce<8;
            bounce++
        ) {

            let nextHit = null;
            let nextFace = null;


            for(const edge of edges) {

                const inter =
                    getSegmentIntersection(
                        currentPoint,
                        currentDir,
                        edge.a,
                        edge.b
                    );


                if(inter) {

                    if(
                        !nextHit ||
                        inter.t < nextHit.t
                    ) {

                        nextHit = inter;
                        nextFace = edge;

                    }

                }

            }


            if(
                !nextHit ||
                !nextFace
            ) {

                drawLine(
                    currentPoint,
                    add(
                        currentPoint,
                        mul(currentDir,800)
                    ),
                    "#e53935",
                    4
                );

                return;

            }


            drawLine(
                currentPoint,
                nextHit.point,
                "#e53935",
                4
            );


            const outwardNormal =
                getOutwardNormal(
                    nextFace,
                    prismCenter
                );


            const exitRefraction =
                refract(
                    currentDir,
                    outwardNormal,
                    currentMedium,
                    1.0
                );


            if(
                exitRefraction.totalInternalReflection ||
                !exitRefraction.ray
            ) {

                currentDir =
                    reflectRay(
                        currentDir,
                        outwardNormal
                    );


                currentPoint = {

                    x:
                        nextHit.point.x +
                        currentDir.x*0.01,

                    y:
                        nextHit.point.y +
                        currentDir.y*0.01

                };


                continue;

            }


            drawLine(
                nextHit.point,
                add(
                    nextHit.point,
                    mul(
                        exitRefraction.ray,
                        800
                    )
                ),
                "#e53935",
                4
            );


            return;

        }

    }

}


/* =========================================================
   화면 표시
   ========================================================= */

function updateVisibility() {

    const type =
        objectType.value;


    const isLens =
        type==="convexLens" ||
        type==="concaveLens";


    lensThicknessRow.style.display =
        isLens
        ? "grid"
        : "none";


    radiusRow.style.display =
        (
            type==="concaveMirror" ||
            type==="convexMirror"
        )
        ? "grid"
        : "none";


    prismRow.style.display =
        type==="prism"
        ? "grid"
        : "none";

}


function render() {

    ctx.clearRect(
        0,
        0,
        W,
        H
    );


    drawAxis();


    const type =
        objectType.value;


    if(type==="convexLens")
        drawConvexLens();

    else if(type==="concaveLens")
        drawConcaveLens();

    else if(type==="planeMirror")
        drawPlaneMirror();

    else if(type==="concaveMirror")
        drawConcaveMirror();

    else if(type==="convexMirror")
        drawConvexMirror();

    else if(type==="prism")
        drawPrism();


    drawLaserAndHandle();

    traceRays();

}


/* =========================================================
   마우스 조작
   ========================================================= */

canvas.addEventListener(
    "mousedown",
    (e) => {

        const mouse =
            getCanvasMousePos(e);


        const lHandle =
            laserHandlePos();


        if(
            Math.hypot(
                mouse.x-lHandle.x,
                mouse.y-lHandle.y
            )<25
        ) {

            draggingLaserHandle = true;

            return;

        }


        const hLimit =
            parseFloat(
                deviceSize.value
            )/2;


        if(
            mouse.x>=objectXPos-70 &&
            mouse.x<=objectXPos+70 &&
            mouse.y>=axisY-hLimit-30 &&
            mouse.y<=axisY+hLimit+30
        ) {

            draggingDevice = true;

            return;

        }

    }
);


window.addEventListener(
    "mousemove",
    (e) => {

        if(
            !draggingLaserHandle &&
            !draggingDevice
        )
            return;


        const mouse =
            getCanvasMousePos(e);


        if(
            draggingLaserHandle
        ) {

            laser.angle =
                Math.atan2(
                    mouse.y-laser.y,
                    mouse.x-laser.x
                );

            render();

        }


        else if(
            draggingDevice
        ) {

            objectXPos =
                Math.max(
                    300,
                    Math.min(
                        950,
                        mouse.x
                    )
                );

            render();

        }

    }
);


window.addEventListener(
    "mouseup",
    () => {

        draggingLaserHandle = false;
        draggingDevice = false;

    }
);


/* =========================================================
   컨트롤
   ========================================================= */

objectType.addEventListener(
    "change",
    () => {

        updateVisibility();
        render();

    }
);


deviceSize.addEventListener(
    "input",
    () => {

        document.getElementById(
            "deviceSizeValue"
        ).innerText =
            deviceSize.value;

        render();

    }
);


lensThickness.addEventListener(
    "input",
    () => {

        document.getElementById(
            "lensThicknessValue"
        ).innerText =
            lensThickness.value;

        render();

    }
);


radius.addEventListener(
    "input",
    () => {

        document.getElementById(
            "radiusValue"
        ).innerText =
            radius.value;

        render();

    }
);


prismAngle.addEventListener(
    "input",
    () => {

        document.getElementById(
            "prismAngleValue"
        ).innerText =
            prismAngle.value+"°";

        render();

    }
);


updateVisibility();
render();

</script>

</body>
</html>
"""


components.html(
    html_code,
    height=920,
    scrolling=True
)
