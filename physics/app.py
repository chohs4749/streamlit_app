import streamlit as str_module
import streamlit.components.v1 as components

str_module.set_page_config(
    page_title="렌즈,거울,프리즘 실험해보기",
    layout="wide"
)

str_module.title("렌즈,거울,프리즘 실험해보기")

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

        <span
            id="deviceSizeValue"
            class="value"
        >
            220
        </span>

    </div>


    <div
        id="lensThicknessRow"
        class="control-grid"
    >

        <label>렌즈 두께</label>

        <input
            id="lensThickness"
            type="range"
            min="20"
            max="70"
            value="40"
        >

        <span
            id="lensThicknessValue"
            class="value"
        >
            40
        </span>

    </div>


    <div
        id="radiusRow"
        class="control-grid"
        style="display:none;"
    >

        <label>거울 곡률반지름 (R)</label>

        <input
            id="radius"
            type="range"
            min="100"
            max="350"
            value="220"
        >

        <span
            id="radiusValue"
            class="value"
        >
            220
        </span>

    </div>


    <div
        id="prismRow"
        class="control-grid"
        style="display:none;"
    >

        <label>프리즘 꼭짓각</label>

        <input
            id="prismAngle"
            type="range"
            min="30"
            max="80"
            value="60"
        >

        <span
            id="prismAngleValue"
            class="value"
        >
            60°
        </span>

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


/* =========================================================
   기본 벡터 함수
   ========================================================= */

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


/* =========================================================
   선 그리기
   ========================================================= */

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


/* =========================================================
   레이저
   ========================================================= */

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
   렌즈 기하
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

    /*
     * 렌즈 가장자리와 중앙의 곡률을
     * 안정적으로 유지하기 위한 곡률반지름
     */
    const halfH = h/2;
    const halfT = th/2;

    const R =
        (
            halfH*halfH +
            halfT*halfT
        ) /
        (2*halfT);

    return {

        x,
        h,
        th,
        R

    };

}


/* =========================================================
   볼록렌즈 모양
   ========================================================= */

function drawConvexLens() {

    const g =
        getLensGeometry();

    const xLeft =
        g.x - g.th/2;

    const xRight =
        g.x + g.th/2;

    const yTop =
        axisY - g.h/2;

    const yBottom =
        axisY + g.h/2;


    ctx.beginPath();

    ctx.moveTo(
        xLeft,
        yTop
    );

    ctx.quadraticCurveTo(
        g.x + g.th/2,
        axisY,
        xLeft,
        yBottom
    );

    ctx.lineTo(
        xRight,
        yBottom
    );

    ctx.quadraticCurveTo(
        g.x - g.th/2,
        axisY,
        xRight,
        yTop
    );

    ctx.closePath();


    ctx.fillStyle =
        "rgba(100,200,255,0.35)";

    ctx.fill();

    ctx.strokeStyle =
        "#0288d1";

    ctx.lineWidth = 3;

    ctx.stroke();

}


/* =========================================================
   오목렌즈 모양
   ========================================================= */

function drawConcaveLens() {

    const g =
        getLensGeometry();

    const xLeft =
        g.x - g.th/2;

    const xRight =
        g.x + g.th/2;

    const yTop =
        axisY - g.h/2;

    const yBottom =
        axisY + g.h/2;


    ctx.beginPath();

    ctx.moveTo(
        xLeft,
        yTop
    );

    ctx.lineTo(
        xRight,
        yTop
    );

    ctx.quadraticCurveTo(
        g.x - g.th/2,
        axisY,
        xRight,
        yBottom
    );

    ctx.lineTo(
        xLeft,
        yBottom
    );

    ctx.quadraticCurveTo(
        g.x + g.th/2,
        axisY,
        xLeft,
        yTop
    );

    ctx.closePath();


    ctx.fillStyle =
        "rgba(100,200,255,0.35)";

    ctx.fill();

    ctx.strokeStyle =
        "#0288d1";

    ctx.lineWidth = 3;

    ctx.stroke();

}


/* =========================================================
   거울
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

    ctx.strokeStyle =
        "#37474f";

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

    ctx.strokeStyle =
        "#37474f";

    ctx.lineWidth = 5;

    ctx.stroke();

}


/* =========================================================
   프리즘
   ========================================================= */

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

    ctx.strokeStyle =
        "#0288d1";

    ctx.lineWidth = 4;

    ctx.stroke();

}


/* =========================================================
   선분 교차
   ========================================================= */

function getSegmentIntersection(
    p,
    d,
    a,
    b
) {

    const v =
        sub(b,a);

    const cross =
        d.x*(-v.y) -
        d.y*(-v.x);

    if(
        Math.abs(cross)<1e-6
    )
        return null;


    const ap =
        sub(a,p);

    const t =
        (
            ap.x*(-v.y) -
            ap.y*(-v.x)
        ) /
        cross;

    const s =
        (
            d.x*ap.y -
            d.y*ap.x
        ) /
        cross;


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


/* =========================================================
   원과 광선 교차
   ========================================================= */

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


    for(
        let t of ts
    ) {

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

        let ang = angle;


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


/* =========================================================
   렌즈 표면 교차
   ========================================================= */

function rayLensSurfaceIntersection(
    p,
    d,
    cx,
    cy,
    R,
    hLimit,
    side
) {

    const L =
        sub(
            p,
            {
                x:cx,
                y:cy
            }
        );


    const B =
        2*dot(L,d);

    const C =
        dot(L,L) -
        R*R;


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


    const ts =
        [t1,t2]
        .filter(
            t=>t>1e-4
        )
        .sort(
            (a,b)=>a-b
        );


    for(
        let t of ts
    ) {

        const hit =
            add(
                p,
                mul(d,t)
            );


        /*
         * 렌즈의 실제 높이 범위 안에 있는지 확인
         */
        if(
            Math.abs(
                hit.y-axisY
            ) >
            hLimit+0.5
        )
            continue;


        const radial =
            sub(
                hit,
                {
                    x:cx,
                    y:cy
                }
            );


        /*
         * left/right 표면의 올바른 원호만 사용
         */
        if(side==="rightmost") {

            if(radial.x < -1e-6)
                continue;

        }

        if(side==="leftmost") {

            if(radial.x > 1e-6)
                continue;

        }


        return {

            t,
            point:hit

        };

    }


    return null;

}


/* =========================================================
   스넬의 법칙
   ========================================================= */

function refract(
    I,
    N,
    n1,
    n2
) {

    I =
        normalize(I);

    N =
        normalize(N);


    let cosI =
        -dot(I,N);


    /*
     * 법선 방향 자동 보정
     */
    if(cosI<0) {

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
        eta*eta*
        (
            1 -
            cosI*cosI
        );


    /*
     * 전반사
     */
    if(
        sin2T>1
    ) {

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
                eta*cosI -
                cosT
            )*N.x,

        y:
            eta*I.y +
            (
                eta*cosI -
                cosT
            )*N.y

    };


    return {

        ray:
            normalize(T),

        totalInternalReflection:false

    };

}


/* =========================================================
   반사
   ========================================================= */

function reflectRay(
    I,
    N
) {

    I =
        normalize(I);

    N =
        normalize(N);


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
   삼각형 바깥쪽 법선
   ========================================================= */

function getOutwardNormal(
    edge,
    center
) {

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
        )>0
    ) {

        n = {

            x:-n.x,
            y:-n.y

        };

    }


    return n;

}


/* =========================================================
   렌즈 광선 추적
   ========================================================= */

function traceLensRays(
    type,
    p,
    d,
    hLimit
) {

    const g =
        getLensGeometry();


    /*
     * =====================================================
     * 볼록렌즈
     * =====================================================
     */

    if(
        type==="convexLens"
    ) {

        /*
         * 왼쪽 면
         *
         * 중심이 렌즈 왼쪽에 있는 원의
         * 오른쪽 원호를 사용
         */
        const leftCx =
            g.x -
            g.th/2 -
            g.R;


        /*
         * 오른쪽 면
         *
         * 중심이 렌즈 오른쪽에 있는 원의
         * 왼쪽 원호를 사용
         */
        const rightCx =
            g.x +
            g.th/2 +
            g.R;


        const hitInRes =
            rayLensSurfaceIntersection(
                p,
                d,
                leftCx,
                axisY,
                g.R,
                hLimit,
                "rightmost"
            );


        if(!hitInRes) {

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


        const hitIn =
            hitInRes.point;


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
         * 입사 전
         */
        drawLine(
            p,
            hitIn,
            "#e53935",
            4
        );


        /*
         * 첫 번째 면의 바깥쪽 법선
         *
         * 볼록렌즈 왼쪽 면에서는
         * 원의 중심 → 입사점 방향이
         * 렌즈 내부를 향하므로 반대로 사용
         */
        const radialIn =
            normalize({

                x:
                    hitIn.x-leftCx,

                y:
                    hitIn.y-axisY

            });


        const outwardIn = {

            x:-radialIn.x,
            y:-radialIn.y

        };


        /*
         * 공기 → 유리
         */
        const firstRefraction =
            refract(
                d,
                outwardIn,
                1.0,
                1.5
            );


        if(
            !firstRefraction.ray
        ) {

            drawLine(
                hitIn,
                add(
                    hitIn,
                    mul(
                        reflectRay(
                            d,
                            outwardIn
                        ),
                        800
                    )
                ),
                "#e53935",
                4
            );

            return;

        }


        const insideDir =
            firstRefraction.ray;


        /*
         * 렌즈 내부에서 오른쪽 면까지 추적
         */
        const hitOutRes =
            rayLensSurfaceIntersection(
                {
                    x:
                        hitIn.x +
                        insideDir.x*0.01,

                    y:
                        hitIn.y +
                        insideDir.y*0.01
                },
                insideDir,
                rightCx,
                axisY,
                g.R,
                hLimit,
                "leftmost"
            );


        if(!hitOutRes) {

            drawLine(
                hitIn,
                add(
                    hitIn,
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


        const hitOut =
            hitOutRes.point;


        /*
         * ★ 핵심
         *
         * 렌즈 안에서도 굴절된 광선을 실제로 그림.
         */
        drawLine(
            hitIn,
            hitOut,
            "#e53935",
            4
        );


        /*
         * 두 번째 면의 바깥쪽 법선
         */
        const radialOut =
            normalize({

                x:
                    hitOut.x-rightCx,

                y:
                    hitOut.y-axisY

            });


        const outwardOut = {

            x:radialOut.x,
            y:radialOut.y

        };


        /*
         * 유리 → 공기
         */
        const secondRefraction =
            refract(
                insideDir,
                outwardOut,
                1.5,
                1.0
            );


        if(
            secondRefraction.totalInternalReflection
        ) {

            const reflected =
                reflectRay(
                    insideDir,
                    outwardOut
                );


            drawLine(
                hitOut,
                add(
                    hitOut,
                    mul(
                        reflected,
                        800
                    )
                ),
                "#e53935",
                4
            );

            return;

        }


        const finalDir =
            secondRefraction.ray;


        /*
         * 두 번째 면을 통과한 실제 굴절광선
         */
        drawLine(
            hitOut,
            add(
                hitOut,
                mul(
                    finalDir,
                    800
                )
            ),
            "#e53935",
            4
        );


        return;

    }


    /*
     * =====================================================
     * 오목렌즈
     * =====================================================
     */

    if(
        type==="concaveLens"
    ) {

        /*
         * 왼쪽 면
         *
         * 중심이 렌즈 안쪽에 있는 원의
         * 왼쪽 원호
         */
        const leftCx =
            g.x -
            g.th/2 +
            g.R;


        /*
         * 오른쪽 면
         *
         * 중심이 렌즈 안쪽에 있는 원의
         * 오른쪽 원호
         */
        const rightCx =
            g.x +
            g.th/2 -
            g.R;


        const hitInRes =
            rayLensSurfaceIntersection(
                p,
                d,
                leftCx,
                axisY,
                g.R,
                hLimit,
                "leftmost"
            );


        if(!hitInRes) {

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


        const hitIn =
            hitInRes.point;


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
         * 입사 전 실제 광선
         */
        drawLine(
            p,
            hitIn,
            "#e53935",
            4
        );


        /*
         * 왼쪽 오목면의 법선
         *
         * 오목렌즈 왼쪽 면에서는
         * 원 중심 → 입사점 방향이
         * 바깥쪽을 향한다.
         */
        const radialIn =
            normalize({

                x:
                    hitIn.x-leftCx,

                y:
                    hitIn.y-axisY

            });


        const outwardIn =
            radialIn;


        /*
         * 공기 → 유리
         */
        const firstRefraction =
            refract(
                d,
                outwardIn,
                1.0,
                1.5
            );


        if(
            !firstRefraction.ray
        ) {

            drawLine(
                hitIn,
                add(
                    hitIn,
                    mul(
                        reflectRay(
                            d,
                            outwardIn
                        ),
                        800
                    )
                ),
                "#e53935",
                4
            );

            return;

        }


        const insideDir =
            firstRefraction.ray;


        /*
         * 오른쪽 면 찾기
         */
        const hitOutRes =
            rayLensSurfaceIntersection(
                {
                    x:
                        hitIn.x +
                        insideDir.x*0.01,

                    y:
                        hitIn.y +
                        insideDir.y*0.01
                },
                insideDir,
                rightCx,
                axisY,
                g.R,
                hLimit,
                "rightmost"
            );


        if(!hitOutRes) {

            drawLine(
                hitIn,
                add(
                    hitIn,
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


        const hitOut =
            hitOutRes.point;


        /*
         * ★ 렌즈 내부에서 실제 굴절된 광선
         */
        drawLine(
            hitIn,
            hitOut,
            "#e53935",
            4
        );


        /*
         * 오른쪽 오목면 법선
         */
        const radialOut =
            normalize({

                x:
                    hitOut.x-rightCx,

                y:
                    hitOut.y-axisY

            });


        const outwardOut =
            radialOut;


        /*
         * 유리 → 공기
         */
        const secondRefraction =
            refract(
                insideDir,
                outwardOut,
                1.5,
                1.0
            );


        if(
            secondRefraction.totalInternalReflection
        ) {

            const reflected =
                reflectRay(
                    insideDir,
                    outwardOut
                );


            drawLine(
                hitOut,
                add(
                    hitOut,
                    mul(
                        reflected,
                        800
                    )
                ),
                "#e53935",
                4
            );

            return;

        }


        const finalDir =
            secondRefraction.ray;


        /*
         * 렌즈를 빠져나온 실제 발산광선
         */
        drawLine(
            hitOut,
            add(
                hitOut,
                mul(
                    finalDir,
                    800
                )
            ),
            "#e53935",
            4
        );


        return;

    }

}


/* =========================================================
   거울 / 프리즘 광선 추적
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


    /*
     * 렌즈
     */
    if(
        type==="convexLens" ||
        type==="concaveLens"
    ) {

        traceLensRays(
            type,
            p,
            d,
            hLimit
        );

        return;

    }


    /* =====================================================
       평면거울
       ===================================================== */

    if(
        type==="planeMirror"
    ) {

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
                    mul(
                        outDir,
                        800
                    )
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

    if(
        type==="concaveMirror"
    ) {

        const specs =
            getConcaveMirrorSpecs();


        const hitResult =
            rayCircleIntersectionStrict(
                p,
                d,
                specs
            );


        if(
            hitResult!==null
        ) {

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


            const outDir =
                reflectRay(
                    d,
                    normal
                );


            drawLine(
                actualHit,
                add(
                    actualHit,
                    mul(
                        outDir,
                        800
                    )
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

    if(
        type==="convexMirror"
    ) {

        const specs =
            getConvexMirrorSpecs();


        const hitResult =
            rayCircleIntersectionStrict(
                p,
                d,
                specs
            );


        if(
            hitResult!==null
        ) {

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


            const outDir =
                reflectRay(
                    d,
                    normal
                );


            drawLine(
                actualHit,
                add(
                    actualHit,
                    mul(
                        outDir,
                        800
                    )
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

    if(
        type==="prism"
    ) {

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

            y:
                axisY-height/2

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
                    Vbl.x+
                    Vtop.x+
                    Vbr.x
                )/3,

            y:
                (
                    Vbl.y+
                    Vtop.y+
                    Vbr.y
                )/3

        };


        let firstHit = null;
        let firstFace = null;


        for(
            let edge of edges
        ) {

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
                    inter.t <
                    firstHit.t
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
                    mul(
                        reflected,
                        800
                    )
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


            for(
                let edge of edges
            ) {

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
                        inter.t <
                        nextHit.t
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
                        mul(
                            currentDir,
                            800
                        )
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
                        nextHit.point.x+
                        currentDir.x*0.01,

                    y:
                        nextHit.point.y+
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
   UI
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


/* =========================================================
   전체 렌더링
   ========================================================= */

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


    if(
        type==="convexLens"
    )
        drawConvexLens();


    else if(
        type==="concaveLens"
    )
        drawConcaveLens();


    else if(
        type==="planeMirror"
    )
        drawPlaneMirror();


    else if(
        type==="concaveMirror"
    )
        drawConcaveMirror();


    else if(
        type==="convexMirror"
    )
        drawConvexMirror();


    else if(
        type==="prism"
    )
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
   컨트롤 이벤트
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


/* =========================================================
   시작
   ========================================================= */

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
