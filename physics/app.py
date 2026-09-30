import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="레이저 광학 시뮬레이터",
    page_icon="🔴",
    layout="wide"
)

st.title("🔴 레이저 광학 시뮬레이터")

st.markdown(
    """
    레이저 손잡이를 드래그하여 입사 방향을 바꿀 수 있습니다.
    렌즈와 거울, 프리즘의 위치와 물리적 조건을 변화시키면서
    반사와 굴절을 관찰할 수 있습니다.
    """
)

html = r"""
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
    border-top: 2px dashed #777;
}

.normal-line {
    width: 40px;
    border-top: 2px dashed #1976d2;
}

.info {
    line-height: 1.8;
    font-size: 15px;
}

.highlight {
    font-weight: bold;
    color: #1565c0;
}

.virtual {
    color: #666;
}

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

        <span id="materialValue" class="value">
            n = 1.52
        </span>

    </div>


    <div id="thicknessRow" class="control-grid">

        <label>렌즈 중심 두께</label>

        <input
            id="thickness"
            type="range"
            min="30"
            max="140"
            value="70"
        >

        <span id="thicknessValue" class="value">
            70
        </span>

    </div>


    <div id="radiusRow" class="control-grid">

        <label>거울 곡률반지름</label>

        <input
            id="radius"
            type="range"
            min="180"
            max="500"
            value="300"
        >

        <span id="radiusValue" class="value">
            300
        </span>

    </div>


    <div id="prismRow" class="control-grid">

        <label>프리즘 꼭짓각</label>

        <input
            id="prismAngle"
            type="range"
            min="30"
            max="80"
            value="60"
        >

        <span id="prismAngleValue" class="value">
            60°
        </span>

    </div>


    <div id="prismMaterialRow" class="control-grid">

        <label>프리즘 굴절률</label>

        <input
            id="prismIndex"
            type="range"
            min="1.10"
            max="2.00"
            step="0.01"
            value="1.52"
        >

        <span id="prismIndexValue" class="value">
            1.52
        </span>

    </div>


    <div class="control-grid">

        <label>광학 기구 위치</label>

        <input
            id="position"
            type="range"
            min="350"
            max="850"
            value="650"
        >

        <span id="positionValue" class="value">
            650
        </span>

    </div>

</div>


<div class="panel">

    <canvas
        id="canvas"
        width="1100"
        height="650">
    </canvas>


    <div class="legend">

        <div class="legend-item">
            <span class="real-line"></span>
            실제 광선
        </div>

        <div class="legend-item">
            <span class="virtual-line"></span>
            광선의 연장 / 허상
        </div>

        <div class="legend-item">
            <span class="normal-line"></span>
            법선
        </div>

    </div>

</div>


<div class="panel info">

    <div>
        <b>현재 광학 기구:</b>
        <span id="objectInfo">볼록렌즈</span>
    </div>

    <div>
        <b>레이저 방향:</b>
        <span id="angleInfo">0°</span>
    </div>

    <div>
        <b>광학 기구 위치:</b>
        <span id="positionInfo">650</span>
    </div>

    <div id="physicsInfo"></div>

    <div>
        <b>광선 작도:</b>
        <span id="imageInfo"></span>
    </div>

    <br>

    <div>
        <b>사용법</b>
    </div>

    <div>
        노란색 손잡이를 마우스로 드래그하면 레이저의 방향이 바뀝니다.
    </div>

    <div>
        실제로 진행하는 빛은 <b>빨간 실선</b>,
        눈으로 직접 볼 수 없는 광선의 연장선은
        <b>회색 점선</b>으로 나타냅니다.
    </div>

</div>


<script>


/* =========================================================
   기본 설정
========================================================= */

const canvas =
    document.getElementById("canvas");

const ctx =
    canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

const axisY = H / 2;


/*
    레이저 발생 위치

    레이저는 기본적으로 왼쪽에서
    오른쪽 방향으로 발사된다.
*/

const laser = {

    x: 90,

    y: axisY,

    angle: 0

};


let dragging = false;


/* =========================================================
   컨트롤
========================================================= */

const objectType =
    document.getElementById("objectType");

const material =
    document.getElementById("material");

const thickness =
    document.getElementById("thickness");

const radius =
    document.getElementById("radius");

const prismAngle =
    document.getElementById("prismAngle");

const position =
    document.getElementById("position");

const prismIndex =
    document.getElementById("prismIndex");


const materialRow =
    document.getElementById("materialRow");

const thicknessRow =
    document.getElementById("thicknessRow");

const radiusRow =
    document.getElementById("radiusRow");

const prismRow =
    document.getElementById("prismRow");

const prismMaterialRow =
    document.getElementById(
        "prismMaterialRow"
    );


/* =========================================================
   벡터
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


function dot(a,b) {

    return a.x*b.x+a.y*b.y;

}


function length(a) {

    return Math.sqrt(
        a.x*a.x+a.y*a.y
    );

}


function normalize(a) {

    const l=length(a);

    if(l===0) {

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

    if(dashed) {

        ctx.setLineDash(
            [10,8]
        );

    }
    else {

        ctx.setLineDash([]);

    }

    ctx.moveTo(
        p1.x,
        p1.y
    );

    ctx.lineTo(
        p2.x,
        p2.y
    );

    ctx.strokeStyle=color;

    ctx.lineWidth=width;

    ctx.stroke();

    ctx.setLineDash([]);

}


/* =========================================================
   글자
========================================================= */

function drawText(
    value,
    x,
    y,
    size=16,
    color="#222"
) {

    ctx.fillStyle=color;

    ctx.font=
        "bold "+size+"px Arial";

    ctx.fillText(
        value,
        x,
        y
    );

}


/* =========================================================
   반사
========================================================= */

function reflect(I,N) {

    I=normalize(I);
    N=normalize(N);

    return normalize(
        sub(
            I,
            mul(
                N,
                2*dot(I,N)
            )
        )
    );

}


/* =========================================================
   스넰의 법칙
========================================================= */

function refract(
    I,
    N,
    n1,
    n2
) {

    I=normalize(I);
    N=normalize(N);

    let cosi=
        Math.max(
            -1,
            Math.min(
                1,
                dot(I,N)
            )
        );

    let etai=n1;
    let etat=n2;

    let normal=N;

    if(cosi < 0) {

        cosi=-cosi;

    }
    else {

        const temp=etai;

        etai=etat;
        etat=temp;

        normal=
            mul(
                N,
                -1
            );

    }


    const eta=
        etai/etat;

    const k=
        1-
        eta*eta*
        (1-cosi*cosi);


    /*
       전반사
    */

    if(k<0) {

        return null;

    }


    return normalize(
        add(
            mul(I,eta),

            mul(
                normal,
                eta*cosi-
                Math.sqrt(k)
            )
        )
    );

}


/* =========================================================
   광선과 수직선 교점
========================================================= */

function rayVertical(
    p,
    d,
    x
) {

    if(
        Math.abs(d.x)<1e-8
    ) {

        return null;

    }

    const t=
        (x-p.x)/d.x;


    if(t<=0.0001) {

        return null;

    }


    return {

        t:t,

        point:
            add(
                p,
                mul(d,t)
            )

    };

}


/* =========================================================
   광선과 원 교점
========================================================= */

function rayCircle(
    p,
    d,
    center,
    R
) {

    const oc=
        sub(
            p,
            center
        );


    const b=
        2*dot(
            d,
            oc
        );


    const c=
        dot(oc,oc)-
        R*R;


    const discriminant=
        b*b-
        4*c;


    if(discriminant<0) {

        return null;

    }


    const root=
        Math.sqrt(
            discriminant
        );


    const t1=
        (-b-root)/2;

    const t2=
        (-b+root)/2;


    let t=null;


    if(t1>0.0001) {

        t=t1;

    }
    else if(t2>0.0001) {

        t=t2;

    }


    if(t===null) {

        return null;

    }


    return {

        t:t,

        point:
            add(
                p,
                mul(d,t)
            )

    };

}


/* =========================================================
   광선과 선분 교점
========================================================= */

function raySegment(
    p,
    d,
    a,
    b
) {

    const v=
        sub(
            b,
            a
        );


    const denominator=
        d.x*v.y-
        d.y*v.x;


    if(
        Math.abs(
            denominator
        )<1e-9
    ) {

        return null;

    }


    const ap=
        sub(
            a,
            p
        );


    const t=
        (
            ap.x*v.y-
            ap.y*v.x
        )/
        denominator;


    const u=
        (
            ap.x*d.y-
            ap.y*d.x
        )/
        denominator;


    if(
        t>0.0001 &&
        u>=0 &&
        u<=1
    ) {

        return {

            t:t,

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
   광학기구 위치
========================================================= */

function objectX() {

    return parseFloat(
        position.value
    );

}


/* =========================================================
   레이저 손잡이
========================================================= */

function handlePosition() {

    return {

        x:
            laser.x+
            Math.cos(
                laser.angle
            )*75,

        y:
            laser.y+
            Math.sin(
                laser.angle
            )*75

    };

}


/* =========================================================
   레이저
========================================================= */

function drawLaser() {

    const handle=
        handlePosition();


    /*
       레이저 본체
    */

    ctx.beginPath();

    ctx.arc(
        laser.x,
        laser.y,
        24,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#333";

    ctx.fill();


    ctx.strokeStyle="#111";

    ctx.lineWidth=3;

    ctx.stroke();


    /*
       노란 손잡이
    */

    drawLine(
        {
            x:laser.x,
            y:laser.y
        },

        handle,

        "#fbc02d",
        14
    );


    ctx.beginPath();

    ctx.arc(
        handle.x,
        handle.y,
        15,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#ffdf3f";

    ctx.fill();

    ctx.strokeStyle="#806000";

    ctx.lineWidth=2;

    ctx.stroke();


    /*
       레이저 발생점
    */

    ctx.beginPath();

    ctx.arc(
        laser.x,
        laser.y,
        7,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#ff0000";

    ctx.fill();


    drawText(
        "드래그",
        handle.x-25,
        handle.y-22,
        13,
        "#555"
    );

}


/* =========================================================
   광축
========================================================= */

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
   초점 표시
========================================================= */

function drawFocus(
    x,
    y,
    label="F"
) {

    ctx.beginPath();

    ctx.arc(
        x,
        y,
        7,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#1976d2";

    ctx.fill();


    drawText(
        label,
        x+10,
        y-10,
        18,
        "#1976d2"
    );

}


/* =========================================================
   평면거울
========================================================= */

function drawPlaneMirror() {

    const x=
        objectX();


    drawLine(
        {
            x:x,
            y:90
        },

        {
            x:x,
            y:560
        },

        "#333",
        9
    );


    for(
        let y=100;
        y<550;
        y+=25
    ) {

        drawLine(
            {
                x:x+6,
                y:y
            },

            {
                x:x+23,
                y:y+17
            },

            "#888",
            2
        );

    }


    drawText(
        "평면거울",
        x-42,
        70,
        18
    );

}


/* =========================================================
   평면거울 광선
========================================================= */

function tracePlaneMirror() {

    const x=
        objectX();


    const p={
        x:laser.x,
        y:laser.y
    };


    const d={
        x:Math.cos(
            laser.angle
        ),

        y:Math.sin(
            laser.angle
        )
    };


    const hit=
        rayVertical(
            p,
            d,
            x
        );


    if(!hit) {

        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            5
        );

        return;

    }


    if(
        hit.point.y<90 ||
        hit.point.y>560
    ) {

        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       입사광
    */

    drawLine(
        p,
        hit.point,
        "#e53935",
        5
    );


    /*
       법선
    */

    drawLine(
        {
            x:hit.point.x-80,
            y:hit.point.y
        },

        {
            x:hit.point.x+80,
            y:hit.point.y
        },

        "#1976d2",
        2,
        true
    );


    /*
       반사광
    */

    const reflected=
        reflect(
            d,
            {
                x:-1,
                y:0
            }
        );


    drawLine(
        hit.point,

        add(
            hit.point,
            mul(
                reflected,
                650
            )
        ),

        "#e53935",
        5
    );


    /*
       거울 뒤쪽으로
       반사광선을 역방향 연장

       평면거울의 가상적인 광선 경로
    */

    drawLine(
        hit.point,

        add(
            hit.point,
            mul(
                reflected,
                -450
            )
        ),

        "#777",
        2,
        true
    );


    drawText(
        "허상 방향",
        x+35,
        hit.point.y-15,
        14,
        "#777"
    );

}


/* =========================================================
   곡면거울
========================================================= */

function curvedMirrorCenter(type) {

    const x=
        objectX();

    const R=
        parseFloat(
            radius.value
        );


    if(
        type==="concaveMirror"
    ) {

        return {

            x:x+R,
            y:axisY

        };

    }


    return {

        x:x-R,
        y:axisY

    };

}


/* =========================================================
   곡면거울 그리기
========================================================= */

function drawCurvedMirror(type) {

    const center=
        curvedMirrorCenter(
            type
        );


    const R=
        parseFloat(
            radius.value
        );


    ctx.beginPath();


    if(
        type==="concaveMirror"
    ) {

        ctx.arc(
            center.x,
            center.y,
            R,
            Math.PI-0.75,
            Math.PI+0.75
        );

    }
    else {

        ctx.arc(
            center.x,
            center.y,
            R,
            -0.75,
            0.75
        );

    }


    ctx.strokeStyle="#333";

    ctx.lineWidth=9;

    ctx.stroke();


    drawText(
        type==="concaveMirror"
        ? "오목거울"
        : "볼록거울",

        objectX()-45,
        70,
        18
    );


    /*
       곡률 중심 C
    */

    drawFocus(
        center.x,
        center.y,
        "C"
    );


    /*
       초점

       거울의 초점거리는
       곡률반지름의 약 절반
    */

    const f=
        R/2;


    if(
        type==="concaveMirror"
    ) {

        drawFocus(
            objectX()+f,
            axisY,
            "F"
        );

    }
    else {

        drawFocus(
            objectX()-f,
            axisY,
            "F"
        );

    }

}


/* =========================================================
   곡면거울 광선
========================================================= */

function traceCurvedMirror(type) {

    const p={
        x:laser.x,
        y:laser.y
    };


    const d={
        x:Math.cos(
            laser.angle
        ),

        y:Math.sin(
            laser.angle
        )
    };


    const center=
        curvedMirrorCenter(
            type
        );


    const R=
        parseFloat(
            radius.value
        );


    const hit=
        rayCircle(
            p,
            d,
            center,
            R
        );


    if(!hit) {

        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       거울의 실제 범위
    */

    if(
        Math.abs(
            hit.point.y-axisY
        )>0.75*R
    ) {

        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       입사광
    */

    drawLine(
        p,
        hit.point,
        "#e53935",
        5
    );


    /*
       법선

       구의 중심과
       충돌점을 연결한 선
    */

    const normal=
        normalize(
            sub(
                hit.point,
                center
            )
        );


    drawLine(
        sub(
            hit.point,
            mul(normal,70)
        ),

        add(
            hit.point,
            mul(normal,70)
        ),

        "#1976d2",
        2,
        true
    );


    /*
       반사광
    */

    const reflected=
        reflect(
            d,
            normal
        );


    drawLine(
        hit.point,

        add(
            hit.point,
            mul(
                reflected,
                700
            )
        ),

        "#e53935",
        5
    );


    /*
       볼록거울의 경우
       실제 반사광선을 뒤로 연장
    */

    if(
        type==="convexMirror"
    ) {

        drawLine(
            hit.point,

            add(
                hit.point,
                mul(
                    reflected,
                    -500
                )
            ),

            "#777",
            2,
            true
        );


        drawText(
            "허상",
            objectX()-125,
            hit.point.y-15,
            16,
            "#777"
        );

    }

}


/* =========================================================
   렌즈 정보
========================================================= */

function lensFocalLength(
    type
) {

    const n=
        parseFloat(
            material.value
        );


    /*
       기본적인 렌즈메이커 관계를
       시각화에 사용.

       양면 렌즈의 경우
       R1 = +R
       R2 = -R

       오목렌즈는 부호가 반대.

       중심 두께가 증가하면
       두 굴절면 사이의 위치가
       변하므로 실제 광선 추적도
       달라진다.
    */


    const R=300;


    let power;


    if(
        type==="convexLens"
    ) {

        power=
            (n-1)*
            (2/R);

    }
    else {

        power=
            -(n-1)*
            (2/R);

    }


    if(
        Math.abs(power)<1e-8
    ) {

        return 1000;

    }


    return 1/power;

}


/* =========================================================
   렌즈 표면
========================================================= */

function lensSurfaces(type) {

    const x=
        objectX();


    const T=
        parseFloat(
            thickness.value
        );


    /*
       표면의 꼭짓점

       중심 두께가 증가하면
       두 표면의 위치가 멀어진다.
    */

    const leftVertex=
        x-T/2;

    const rightVertex=
        x+T/2;


    /*
       곡률반지름

       화면에서 교과서적인
       형태가 잘 보이도록 설정
    */

    const R=300;


    if(
        type==="convexLens"
    ) {

        return {

            left:{

                vertex:leftVertex,

                center:{
                    x:leftVertex+R,
                    y:axisY
                },

                R:R

            },

            right:{

                vertex:rightVertex,

                center:{
                    x:rightVertex-R,
                    y:axisY
                },

                R:R

            }

        };

    }


    return {

        left:{

            vertex:leftVertex,

            center:{
                x:leftVertex-R,
                y:axisY
            },

            R:R

        },

        right:{

            vertex:rightVertex,

            center:{
                x:rightVertex+R,
                y:axisY
            },

            R:R

        }

    };

}


/* =========================================================
   렌즈 그리기
========================================================= */

function drawLens(type) {

    const s=
        lensSurfaces(
            type
        );


    const aperture=220;


    ctx.beginPath();


    /*
       왼쪽 면
    */

    for(
        let i=0;
        i<=100;
        i++
    ) {

        const y=
            -aperture+
            2*aperture*i/100;


        const inside=
            Math.max(
                0,
                s.left.R*
                s.left.R-
                y*y
            );


        let x;


        if(
            type==="convexLens"
        ) {

            x=
                s.left.center.x-
                Math.sqrt(inside);

        }
        else {

            x=
                s.left.center.x+
                Math.sqrt(inside);

        }


        const py=
            axisY+y;


        if(i===0) {

            ctx.moveTo(
                x,
                py
            );

        }
        else {

            ctx.lineTo(
                x,
                py
            );

        }

    }


    /*
       오른쪽 면
    */

    for(
        let i=100;
        i>=0;
        i--
    ) {

        const y=
            -aperture+
            2*aperture*i/100;


        const inside=
            Math.max(
                0,
                s.right.R*
                s.right.R-
                y*y
            );


        let x;


        if(
            type==="convexLens"
        ) {

            x=
                s.right.center.x+
                Math.sqrt(inside);

        }
        else {

            x=
                s.right.center.x-
                Math.sqrt(inside);

        }


        const py=
            axisY+y;


        ctx.lineTo(
            x,
            py
        );

    }


    ctx.closePath();


    ctx.fillStyle=
        "rgba(70,160,255,0.22)";

    ctx.fill();


    ctx.strokeStyle="#1565c0";

    ctx.lineWidth=4;

    ctx.stroke();


    drawText(
        type==="convexLens"
        ? "볼록렌즈"
        : "오목렌즈",

        objectX()-45,
        65,
        18
    );


    /*
       초점 표시

       굴절률에 따라
       초점 위치를 변경
    */

    let f=
        Math.abs(
            lensFocalLength(
                type
            )
        );


    /*
       화면 안에서 보기 좋게
       스케일 조정
    */

    f=
        Math.max(
            120,
            Math.min(
                330,
                f
            )
        );


    if(
        type==="convexLens"
    ) {

        drawFocus(
            objectX()+f,
            axisY,
            "F"
        );

        drawFocus(
            objectX()-f,
            axisY,
            "F"
        );

    }
    else {

        drawFocus(
            objectX()-f,
            axisY,
            "F"
        );

    }

}


/* =========================================================
   렌즈 광선
========================================================= */

function traceLens(type) {

    const s=
        lensSurfaces(
            type
        );


    const n=
        parseFloat(
            material.value
        );


    let p={
        x:laser.x,
        y:laser.y
    };


    let d={
        x:Math.cos(
            laser.angle
        ),

        y:Math.sin(
            laser.angle
        )
    };


    /*
       첫 번째 표면
    */

    const first=
        rayCircle(
            p,
            d,
            s.left.center,
            s.left.R
        );


    if(!first) {

        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            5
        );

        return;

    }


    if(
        Math.abs(
            first.point.y-axisY
        )>220
    ) {

        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       입사광
    */

    drawLine(
        p,
        first.point,
        "#e53935",
        5
    );


    /*
       첫 번째 면 법선
    */

    const N1=
        normalize(
            sub(
                first.point,
                s.left.center
            )
        );


    /*
       공기 → 렌즈
    */

    let inside=
        refract(
            d,
            N1,
            1.0,
            n
        );


    if(!inside) {

        inside=
            reflect(
                d,
                N1
            );


        drawLine(
            first.point,
            add(
                first.point,
                mul(
                    inside,
                    600
                )
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       렌즈 내부
    */

    const second=
        rayCircle(
            first.point,
            inside,
            s.right.center,
            s.right.R
        );


    if(!second) {

        drawLine(
            first.point,
            add(
                first.point,
                mul(
                    inside,
                    600
                )
            ),
            "#e53935",
            5
        );

        return;

    }


    drawLine(
        first.point,
        second.point,
        "#e53935",
        5
    );


    /*
       두 번째 면 법선
    */

    const N2=
        normalize(
            sub(
                second.point,
                s.right.center
            )
        );


    /*
       렌즈 → 공기
    */

    let out=
        refract(
            inside,
            N2,
            n,
            1.0
        );


    if(!out) {

        out=
            reflect(
                inside,
                N2
            );

    }


    /*
       최종 굴절광
    */

    drawLine(
        second.point,

        add(
            second.point,
            mul(
                out,
                800
            )
        ),

        "#e53935",
        6
    );


    /*
       오목렌즈의 허초점

       굴절된 광선을 반대 방향으로
       연장하여 표시
    */

    if(
        type==="concaveLens"
    ) {

        drawLine(
            second.point,

            add(
                second.point,
                mul(
                    out,
                    -600
                )
            ),

            "#777",
            2,
            true
        );


        drawText(
            "허초점 F",
            objectX()-170,
            axisY-20,
            16,
            "#777"
        );

    }


    /*
       볼록렌즈

       레이저가 광축과 평행하게
       들어오는 경우 초점으로
       향하도록 시각적으로 강조
    */

    if(
        type==="convexLens" &&
        Math.abs(
            laser.angle
        )<0.03
    ) {

        const f=
            Math.max(
                120,
                Math.min(
                    330,
                    Math.abs(
                        lensFocalLength(
                            type
                        )
                    )
                )
            );


        /*
           실제 계산된 굴절광선과
           초점 위치를 연결하는
           보조 표시
        */

        drawFocus(
            objectX()+f,
            axisY,
            "F"
        );

    }

}


/* =========================================================
   프리즘
========================================================= */

function prismVertices() {

    const x=
        objectX();


    const A=
        parseFloat(
            prismAngle.value
        )*
        Math.PI/180;


    const base=300;


    const height=
        base/
        (
            2*
            Math.tan(
                A/2
            )
        );


    return [

        {
            x:x-base/2,
            y:axisY+height/2
        },

        {
            x:x,
            y:axisY-height/2
        },

        {
            x:x+base/2,
            y:axisY+height/2
        }

    ];

}


/* =========================================================
   프리즘 그리기
========================================================= */

function drawPrism() {

    const v=
        prismVertices();


    ctx.beginPath();

    ctx.moveTo(
        v[0].x,
        v[0].y
    );

    ctx.lineTo(
        v[1].x,
        v[1].y
    );

    ctx.lineTo(
        v[2].x,
        v[2].y
    );

    ctx.closePath();


    ctx.fillStyle=
        "rgba(70,160,255,0.25)";

    ctx.fill();


    ctx.strokeStyle="#1565c0";

    ctx.lineWidth=4;

    ctx.stroke();


    drawText(
        "프리즘",
        objectX()-25,
        v[2].y+38,
        18
    );

}


/* =========================================================
   프리즘 광선
========================================================= */

function tracePrism() {

    const vertices=
        prismVertices();


    const n=
        parseFloat(
            prismIndex.value
        );


    let p={
        x:laser.x,
        y:laser.y
    };


    let d={
        x:Math.cos(
            laser.angle
        ),

        y:Math.sin(
            laser.angle
        )
    };


    const edges=[

        [
            vertices[0],
            vertices[1]
        ],

        [
            vertices[1],
            vertices[2]
        ],

        [
            vertices[2],
            vertices[0]
        ]

    ];


    /*
       첫 번째 면 찾기
    */

    let first=null;

    let firstIndex=-1;


    for(
        let i=0;
        i<edges.length;
        i++
    ) {

        const hit=
            raySegment(
                p,
                d,
                edges[i][0],
                edges[i][1]
            );


        if(
            hit &&
            (
                first===null ||
                hit.t<first.t
            )
        ) {

            first=hit;

            firstIndex=i;

        }

    }


    if(!first) {

        drawLine(
            p,
            add(
                p,
                mul(d,1000)
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       입사광
    */

    drawLine(
        p,
        first.point,
        "#e53935",
        5
    );


    /*
       첫 번째 면의 법선
    */

    const edge1=
        sub(
            edges[firstIndex][1],
            edges[firstIndex][0]
        );


    let N1=
        normalize({
            x:-edge1.y,
            y:edge1.x
        });


    /*
       공기 → 프리즘
    */

    let inside=
        refract(
            d,
            N1,
            1.0,
            n
        );


    if(!inside) {

        inside=
            reflect(
                d,
                N1
            );


        drawLine(
            first.point,
            add(
                first.point,
                mul(
                    inside,
                    600
                )
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       두 번째 면 찾기
    */

    let second=null;

    let secondIndex=-1;


    for(
        let i=0;
        i<edges.length;
        i++
    ) {

        if(
            i===firstIndex
        ) {

            continue;

        }


        const hit=
            raySegment(
                first.point,
                inside,
                edges[i][0],
                edges[i][1]
            );


        if(
            hit &&
            (
                second===null ||
                hit.t<second.t
            )
        ) {

            second=hit;

            secondIndex=i;

        }

    }


    if(!second) {

        drawLine(
            first.point,
            add(
                first.point,
                mul(
                    inside,
                    600
                )
            ),
            "#e53935",
            5
        );

        return;

    }


    /*
       프리즘 내부
    */

    drawLine(
        first.point,
        second.point,
        "#e53935",
        5
    );


    /*
       두 번째 면 법선
    */

    const edge2=
        sub(
            edges[secondIndex][1],
            edges[secondIndex][0]
        );


    let N2=
        normalize({
            x:-edge2.y,
            y:edge2.x
        });


    /*
       프리즘 → 공기
    */

    let out=
        refract(
            inside,
            N2,
            n,
            1.0
        );


    if(!out) {

        out=
            reflect(
                inside,
                N2
            );

    }


    /*
       최종 굴절광

       이 부분에서 한 번만 그린다.
       따라서 프리즘에서 광선이
       두 개 생기는 문제가 없다.
    */

    drawLine(
        second.point,

        add(
            second.point,
            mul(
                out,
                800
            )
        ),

        "#e53935",
        6
    );

}


/* =========================================================
   전체 화면
========================================================= */

function draw() {

    ctx.clearRect(
        0,
        0,
        W,
        H
    );


    ctx.fillStyle="white";

    ctx.fillRect(
        0,
        0,
        W,
        H
    );


    drawAxis();


    const type=
        objectType.value;


    /*
       광학 기구
    */

    if(
        type==="planeMirror"
    ) {

        drawPlaneMirror();

    }

    else if(
        type==="concaveMirror" ||
        type==="convexMirror"
    ) {

        drawCurvedMirror(
            type
        );

    }

    else if(
        type==="convexLens" ||
        type==="concaveLens"
    ) {

        drawLens(
            type
        );

    }

    else if(
        type==="prism"
    ) {

        drawPrism();

    }


    /*
       광선
    */

    if(
        type==="planeMirror"
    ) {

        tracePlaneMirror();

    }

    else if(
        type==="concaveMirror" ||
        type==="convexMirror"
    ) {

        traceCurvedMirror(
            type
        );

    }

    else if(
        type==="convexLens" ||
        type==="concaveLens"
    ) {

        traceLens(
            type
        );

    }

    else if(
        type==="prism"
    ) {

        tracePrism();

    }


    /*
       레이저 본체는
       광선 위에 표시
    */

    drawLaser();


    /*
       정보
    */

    const deg=
        laser.angle*
        180/
        Math.PI;


    document.getElementById(
        "angleInfo"
    ).textContent=
        deg.toFixed(1)+"°";


    document.getElementById(
        "positionInfo"
    ).textContent=
        objectX().toFixed(0);


    document.getElementById(
        "objectInfo"
    ).textContent=
        objectType.options[
            objectType.selectedIndex
        ].text;


    updatePhysicsInfo();

}


/* =========================================================
   물리 설명
========================================================= */

function updatePhysicsInfo() {

    const type=
        objectType.value;


    let text="";


    if(
        type==="convexLens"
    ) {

        const n=
            parseFloat(
                material.value
            );


        text=
        "볼록렌즈에서는 평행하게 들어온 빛이 "
        +"굴절되어 초점 F를 향합니다. "
        +"현재 굴절률 n = "
        +n.toFixed(2)
        +"입니다.";

    }


    else if(
        type==="concaveLens"
    ) {

        text=
        "오목렌즈에서는 빛이 퍼져 나가며, "
        +"굴절된 광선을 뒤쪽으로 연장하면 "
        +"허초점 F에서 나온 것처럼 보입니다.";

    }


    else if(
        type==="planeMirror"
    ) {

        text=
        "평면거울에서는 입사각과 반사각이 같으며, "
        +"반사광선을 거울 뒤쪽으로 연장하면 "
        +"가상적인 광선 경로를 확인할 수 있습니다.";

    }


    else if(
        type==="concaveMirror"
    ) {

        text=
        "오목거울에서는 반사면의 법선을 기준으로 "
        +"반사 법칙을 적용합니다. "
        +"광축과 평행한 광선은 초점 방향으로 반사됩니다.";

    }


    else if(
        type==="convexMirror"
    ) {

        text=
        "볼록거울에서는 반사된 광선이 퍼져 나가며, "
        +"반사광선을 뒤쪽으로 연장하면 "
        +"허초점 방향에서 나온 것처럼 보입니다.";

    }


    else if(
        type==="prism"
    ) {

        const n=
            parseFloat(
                prismIndex.value
            );


        text=
        "프리즘에서는 첫 번째 면에서 굴절되고 "
        +"프리즘 내부를 진행한 뒤 두 번째 면에서 "
        +"다시 굴절됩니다. 현재 굴절률 n = "
        +n.toFixed(2)
        +"입니다.";

    }


    document.getElementById(
        "physicsInfo"
    ).textContent=
        text;


    /*
       광선 작도 설명
    */

    let imageText="";


    if(
        type==="convexLens"
    ) {

        imageText=
            "평행광선 → 초점 F 방향으로 굴절";

    }

    else if(
        type==="concaveLens"
    ) {

        imageText=
            "실제 굴절광선은 퍼짐 → 점선 연장선에서 허초점 확인";

    }

    else if(
        type==="planeMirror"
    ) {

        imageText=
            "반사광선은 실제 광선, 거울 뒤 점선은 가상적인 연장";

    }

    else if(
        type==="convexMirror"
    ) {

        imageText=
            "반사광선의 점선 연장선으로 허초점 확인";

    }

    else if(
        type==="concaveMirror"
    ) {

        imageText=
            "반사광선이 초점 방향으로 진행";

    }

    else {

        imageText=
            "두 굴절면에서 연속적으로 굴절";

    }


    document.getElementById(
        "imageInfo"
    ).textContent=
        imageText;

}


/* =========================================================
   마우스 좌표
========================================================= */

function mousePosition(event) {

    const rect=
        canvas.getBoundingClientRect();


    return {

        x:
            (event.clientX-
             rect.left)
            *
            W/
            rect.width,

        y:
            (event.clientY-
             rect.top)
            *
            H/
            rect.height

    };

}


/* =========================================================
   레이저 손잡이 드래그
========================================================= */

canvas.addEventListener(
    "mousedown",
    function(event) {

        const p=
            mousePosition(
                event
            );


        const h=
            handlePosition();


        const distance=
            Math.sqrt(
                (p.x-h.x)*
                (p.x-h.x)+

                (p.y-h.y)*
                (p.y-h.y)
            );


        if(
            distance<40
        ) {

            dragging=true;

            canvas.style.cursor=
                "grabbing";

        }

    }
);


canvas.addEventListener(
    "mousemove",
    function(event) {

        const p=
            mousePosition(
                event
            );


        const h=
            handlePosition();


        if(!dragging) {

            const distance=
                Math.sqrt(
                    (p.x-h.x)*
                    (p.x-h.x)+

                    (p.y-h.y)*
                    (p.y-h.y)
                );


            canvas.style.cursor=
                distance<40
                ? "grab"
                : "default";


            return;

        }


        /*
           레이저 중심에서
           마우스 위치를 향하는
           각도
        */

        laser.angle=
            Math.atan2(
                p.y-laser.y,
                p.x-laser.x
            );


        draw();

    }
);


window.addEventListener(
    "mouseup",
    function() {

        dragging=false;

        canvas.style.cursor=
            "default";

    }
);


/* =========================================================
   터치
========================================================= */

canvas.addEventListener(
    "touchstart",
    function(event) {

        const touch=
            event.touches[0];


        const rect=
            canvas.getBoundingClientRect();


        const p={

            x:
                (touch.clientX-
                 rect.left)
                *
                W/
                rect.width,

            y:
                (touch.clientY-
                 rect.top)
                *
                H/
                rect.height

        };


        const h=
            handlePosition();


        const distance=
            Math.sqrt(
                (p.x-h.x)*
                (p.x-h.x)+

                (p.y-h.y)*
                (p.y-h.y)
            );


        if(
            distance<50
        ) {

            dragging=true;

        }

    }
);


canvas.addEventListener(
    "touchmove",
    function(event) {

        if(!dragging) {

            return;

        }


        event.preventDefault();


        const touch=
            event.touches[0];


        const rect=
            canvas.getBoundingClientRect();


        const p={

            x:
                (touch.clientX-
                 rect.left)
                *
                W/
                rect.width,

            y:
                (touch.clientY-
                 rect.top)
                *
                H/
                rect.height

        };


        laser.angle=
            Math.atan2(
                p.y-laser.y,
                p.x-laser.x
            );


        draw();

    },

    {
        passive:false
    }
);


canvas.addEventListener(
    "touchend",
    function() {

        dragging=false;

    }
);


/* =========================================================
   컨트롤 변경
========================================================= */

objectType.addEventListener(
    "change",
    updateControls
);


material.addEventListener(
    "input",
    draw
);


thickness.addEventListener(
    "input",
    draw
);


radius.addEventListener(
    "input",
    draw
);


prismAngle.addEventListener(
    "input",
    draw
);


position.addEventListener(
    "input",
    draw
);


prismIndex.addEventListener(
    "input",
    draw
);


/* =========================================================
   값 표시
========================================================= */

thickness.addEventListener(
    "input",
    function() {

        document.getElementById(
            "thicknessValue"
        ).textContent=
            thickness.value;

    }
);


radius.addEventListener(
    "input",
    function() {

        document.getElementById(
            "radiusValue"
        ).textContent=
            radius.value;

    }
);


prismAngle.addEventListener(
    "input",
    function() {

        document.getElementById(
            "prismAngleValue"
        ).textContent=
            prismAngle.value+
            "°";

    }
);


position.addEventListener(
    "input",
    function() {

        document.getElementById(
            "positionValue"
        ).textContent=
            position.value;

    }
);


material.addEventListener(
    "input",
    function() {

        document.getElementById(
            "materialValue"
        ).textContent=
            "n = "+
            parseFloat(
                material.value
            ).toFixed(2);

    }
);


prismIndex.addEventListener(
    "input",
    function() {

        document.getElementById(
            "prismIndexValue"
        ).textContent=
            parseFloat(
                prismIndex.value
            ).toFixed(2);

    }
);


/* =========================================================
   컨트롤 표시
========================================================= */

function updateControls() {

    const type=
        objectType.value;


    const isLens=
        type==="convexLens" ||
        type==="concaveLens";


    const isMirror=
        type==="concaveMirror" ||
        type==="convexMirror";


    const isPrism=
        type==="prism";


    materialRow.style.display=
        isLens
        ? "grid"
        : "none";


    thicknessRow.style.display=
        isLens
        ? "grid"
        : "none";


    radiusRow.style.display=
        isMirror
        ? "grid"
        : "none";


    prismRow.style.display=
        isPrism
        ? "grid"
        : "none";


    prismMaterialRow.style.display=
        isPrism
        ? "grid"
        : "none";


    draw();

}


/* =========================================================
   시작
========================================================= */

updateControls();

</script>

</body>

</html>
"""


components.html(
    html,
    height=1100,
    scrolling=False
)
