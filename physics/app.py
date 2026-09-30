import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="레이저 광학 시뮬레이터",
    page_icon="🔴",
    layout="wide"
)

st.title("🔴 레이저 광학 시뮬레이터")

st.write(
    "레이저 손잡이를 직접 움직여 광선의 방향을 바꾸고, "
    "렌즈·거울·프리즘에서 일어나는 반사와 굴절을 관찰할 수 있습니다."
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
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    color: #222;
}

.panel {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.control-grid {
    display: grid;
    grid-template-columns: 150px 1fr 100px;
    gap: 12px;
    align-items: center;
    margin-bottom: 12px;
}

select,
input[type="range"] {
    width: 100%;
}

select {
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #aaa;
    font-size: 15px;
}

input[type="range"] {
    cursor: pointer;
}

.value {
    font-weight: bold;
    text-align: right;
}

#canvas {
    display: block;
    width: 100%;
    height: auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    cursor: default;
}

.info {
    line-height: 1.8;
}

.warning {
    color: #c62828;
    font-weight: bold;
}

.small {
    color: #666;
    font-size: 13px;
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


    <!-- 렌즈 재질 -->

    <div id="materialRow" class="control-grid">

        <label>렌즈 재질</label>

        <select id="material">

            <option value="1.49">아크릴 / 플라스틱 (n = 1.49)</option>
            <option value="1.52" selected>일반 유리 (n = 1.52)</option>
            <option value="1.62">고굴절 유리 (n = 1.62)</option>

        </select>

        <span id="materialValue" class="value">n = 1.52</span>

    </div>


    <!-- 렌즈 두께 -->

    <div id="thicknessRow" class="control-grid">

        <label>렌즈 중심 두께</label>

        <input
            id="thickness"
            type="range"
            min="30"
            max="150"
            value="80"
        >

        <span id="thicknessValue" class="value">
            80 px
        </span>

    </div>


    <!-- 거울 곡률 -->

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


    <!-- 프리즘 -->

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


    <!-- 위치 -->

    <div class="control-grid">

        <label>광학 기구 위치</label>

        <input
            id="position"
            type="range"
            min="300"
            max="900"
            value="650"
        >

        <span id="positionValue" class="value">
            650
        </span>

    </div>


    <!-- 굴절률 -->

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

</div>


<div class="panel">

    <canvas
        id="canvas"
        width="1100"
        height="650">
    </canvas>

</div>


<div class="panel info">

    <b>실험 정보</b>

    <div>
        광학 기구:
        <b id="objectInfo">볼록렌즈</b>
    </div>

    <div>
        레이저 각도:
        <b id="angleInfo">0°</b>
    </div>

    <div>
        광학 기구 위치:
        <b id="positionInfo">650</b>
    </div>

    <div id="physicsInfo"></div>

    <div class="small">
        💡 노란색 손잡이를 마우스로 직접 드래그하여 레이저 방향을 바꿀 수 있습니다.
    </div>

</div>


<script>

/* =====================================================
   기본 설정
===================================================== */

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

const axisY = H / 2;

const laser = {
    x: 100,
    y: axisY,
    angle: 0
};

let dragging = false;


/* =====================================================
   HTML 요소
===================================================== */

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
    document.getElementById("prismMaterialRow");


/* =====================================================
   벡터 함수
===================================================== */

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

function len(a) {

    return Math.sqrt(
        a.x*a.x+a.y*a.y
    );

}

function norm(a) {

    const l=len(a);

    if(l===0) {
        return {x:1,y:0};
    }

    return {
        x:a.x/l,
        y:a.y/l
    };

}


/* =====================================================
   선 그리기
===================================================== */

function line(
    p1,
    p2,
    color="#ff2020",
    width=3,
    dashed=false
) {

    ctx.beginPath();

    if(dashed) {
        ctx.setLineDash([8,7]);
    }
    else {
        ctx.setLineDash([]);
    }

    ctx.moveTo(p1.x,p1.y);
    ctx.lineTo(p2.x,p2.y);

    ctx.strokeStyle=color;
    ctx.lineWidth=width;

    ctx.stroke();

    ctx.setLineDash([]);

}


/* =====================================================
   글자
===================================================== */

function text(
    value,
    x,
    y,
    size=16,
    color="#222"
) {

    ctx.fillStyle=color;
    ctx.font=size+"px Arial";
    ctx.fillText(value,x,y);

}


/* =====================================================
   반사
===================================================== */

function reflect(I,N) {

    I=norm(I);
    N=norm(N);

    return norm(
        sub(
            I,
            mul(N,2*dot(I,N))
        )
    );

}


/* =====================================================
   스넬의 법칙
===================================================== */

function refract(I,N,n1,n2) {

    I=norm(I);
    N=norm(N);

    let cosi=
        Math.max(
            -1,
            Math.min(1,dot(I,N))
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

        normal=mul(N,-1);

    }

    const eta=etai/etat;

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

    return norm(
        add(
            mul(I,eta),
            mul(
                normal,
                eta*cosi-Math.sqrt(k)
            )
        )
    );

}


/* =====================================================
   광선과 수직선의 교점
===================================================== */

function verticalIntersection(
    p,
    d,
    x
) {

    if(Math.abs(d.x)<1e-8) {
        return null;
    }

    const t=(x-p.x)/d.x;

    if(t<=0.0001) {
        return null;
    }

    return {
        t:t,
        point:add(p,mul(d,t))
    };

}


/* =====================================================
   원과 광선의 교점
===================================================== */

function rayCircleIntersection(
    p,
    d,
    center,
    R
) {

    const oc=sub(p,center);

    const b=2*dot(d,oc);

    const c=dot(oc,oc)-R*R;

    const discriminant=
        b*b-4*c;

    if(discriminant<0) {
        return null;
    }

    const root=
        Math.sqrt(discriminant);

    const t1=(-b-root)/2;
    const t2=(-b+root)/2;

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
        point:add(p,mul(d,t))
    };

}


/* =====================================================
   선분과 광선의 교점
===================================================== */

function raySegmentIntersection(
    p,
    d,
    a,
    b
) {

    const v=sub(b,a);

    const denominator=
        d.x*v.y-
        d.y*v.x;

    if(Math.abs(denominator)<1e-9) {
        return null;
    }

    const ap=sub(a,p);

    const t=
        (ap.x*v.y-ap.y*v.x)/
        denominator;

    const u=
        (ap.x*d.y-ap.y*d.x)/
        denominator;

    if(
        t>0.0001 &&
        u>=0 &&
        u<=1
    ) {

        return {
            t:t,
            point:add(p,mul(d,t))
        };

    }

    return null;

}


/* =====================================================
   광학 기구 위치
===================================================== */

function objectX() {

    return parseFloat(position.value);

}


/* =====================================================
   레이저 손잡이
===================================================== */

function handlePosition() {

    return {

        x:
        laser.x+
        Math.cos(laser.angle)*75,

        y:
        laser.y+
        Math.sin(laser.angle)*75

    };

}


/* =====================================================
   레이저 그리기
===================================================== */

function drawLaser() {

    const dir={
        x:Math.cos(laser.angle),
        y:Math.sin(laser.angle)
    };

    const handle=handlePosition();


    /*
       레이저 본체
    */

    ctx.beginPath();

    ctx.arc(
        laser.x,
        laser.y,
        23,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#333";
    ctx.fill();

    ctx.strokeStyle="#111";
    ctx.lineWidth=3;
    ctx.stroke();


    /*
       손잡이
    */

    line(
        {x:laser.x,y:laser.y},
        handle,
        "#f4b400",
        13
    );


    ctx.beginPath();

    ctx.arc(
        handle.x,
        handle.y,
        14,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#ffd83d";
    ctx.fill();

    ctx.strokeStyle="#806000";
    ctx.lineWidth=2;
    ctx.stroke();


    /*
       레이저 발생 지점
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


    /*
       손잡이 설명
    */

    text(
        "드래그",
        handle.x-25,
        handle.y-20,
        13,
        "#555"
    );

}


/* =====================================================
   광축
===================================================== */

function drawAxis() {

    line(
        {x:30,y:axisY},
        {x:1070,y:axisY},
        "#aaa",
        1,
        true
    );

    text(
        "광축",
        1010,
        axisY-10,
        13,
        "#777"
    );

}


/* =====================================================
   평면거울
===================================================== */

function drawPlaneMirror() {

    const x=objectX();

    line(
        {x:x,y:100},
        {x:x,y:550},
        "#333",
        8
    );


    /*
       뒷면 무늬
    */

    for(
        let y=110;
        y<550;
        y+=25
    ) {

        line(
            {x:x+5,y:y},
            {x:x+20,y:y+15},
            "#888",
            2
        );

    }


    text(
        "평면거울",
        x-38,
        80,
        18
    );

}


/* =====================================================
   평면거울 광선
===================================================== */

function tracePlaneMirror() {

    const x=objectX();

    const d={
        x:Math.cos(laser.angle),
        y:Math.sin(laser.angle)
    };

    const p={
        x:laser.x,
        y:laser.y
    };

    const hit=
        verticalIntersection(
            p,
            d,
            x
        );


    /*
       거울을 향하지 않는 경우
    */

    if(!hit) {

        line(
            p,
            add(p,mul(d,1000)),
            "#ff2020",
            4
        );

        return;

    }


    if(
        hit.point.y<100 ||
        hit.point.y>550
    ) {

        line(
            p,
            add(p,mul(d,1000)),
            "#ff2020",
            4
        );

        return;

    }


    /*
       입사광
    */

    line(
        p,
        hit.point,
        "#ff2020",
        4
    );


    /*
       법선
    */

    line(
        {
            x:hit.point.x-70,
            y:hit.point.y
        },
        {
            x:hit.point.x+70,
            y:hit.point.y
        },
        "#777",
        1,
        true
    );


    /*
       반사
    */

    const reflected=
        reflect(
            d,
            {x:-1,y:0}
        );


    line(
        hit.point,
        add(
            hit.point,
            mul(reflected,600)
        ),
        "#ff2020",
        4
    );

}


/* =====================================================
   곡면거울 그리기
===================================================== */

function drawCurvedMirror(type) {

    const x=objectX();

    const R=
        parseFloat(radius.value);

    const centerX=
        type==="concaveMirror"
        ? x+R
        : x-R;


    ctx.beginPath();


    if(type==="concaveMirror") {

        ctx.arc(
            centerX,
            axisY,
            R,
            Math.PI-0.65,
            Math.PI+0.65
        );

    }
    else {

        ctx.arc(
            centerX,
            axisY,
            R,
            -0.65,
            0.65
        );

    }


    ctx.strokeStyle="#333";
    ctx.lineWidth=8;

    ctx.stroke();


    text(
        type==="concaveMirror"
        ? "오목거울"
        : "볼록거울",
        x-45,
        80,
        18
    );


    /*
       곡률 중심 표시
    */

    ctx.beginPath();

    ctx.arc(
        centerX,
        axisY,
        5,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#1976d2";
    ctx.fill();

}


/* =====================================================
   곡면거울 광선
===================================================== */

function traceCurvedMirror(type) {

    const x=objectX();

    const R=
        parseFloat(radius.value);

    const center={

        x:
        type==="concaveMirror"
        ? x+R
        : x-R,

        y:axisY

    };


    const d={
        x:Math.cos(laser.angle),
        y:Math.sin(laser.angle)
    };

    const p={
        x:laser.x,
        y:laser.y
    };


    const hit=
        rayCircleIntersection(
            p,
            d,
            center,
            R
        );


    if(!hit) {

        line(
            p,
            add(p,mul(d,1000)),
            "#ff2020",
            4
        );

        return;

    }


    /*
       유효한 거울 영역인지 확인
    */

    if(
        Math.abs(
            hit.point.y-axisY
        )>R*0.75
    ) {

        line(
            p,
            add(p,mul(d,1000)),
            "#ff2020",
            4
        );

        return;

    }


    /*
       입사광
    */

    line(
        p,
        hit.point,
        "#ff2020",
        4
    );


    /*
       법선
    */

    const normal=
        norm(
            sub(
                hit.point,
                center
            )
        );


    line(
        sub(
            hit.point,
            mul(normal,60)
        ),
        add(
            hit.point,
            mul(normal,60)
        ),
        "#777",
        1,
        true
    );


    /*
       반사
    */

    const reflected=
        reflect(
            d,
            normal
        );


    line(
        hit.point,
        add(
            hit.point,
            mul(reflected,600)
        ),
        "#ff2020",
        4
    );

}


/* =====================================================
   렌즈의 실제 표면
===================================================== */

function lensSurfaces(type) {

    const x=objectX();

    const T=
        parseFloat(thickness.value);

    const R=300;

    const leftVertex=
        x-T/2;

    const rightVertex=
        x+T/2;


    let leftCenter;
    let rightCenter;


    if(type==="convexLens") {

        /*
           양면 볼록렌즈

           왼쪽 면:
           중심이 오른쪽

           오른쪽 면:
           중심이 왼쪽
        */

        leftCenter=
            leftVertex+R;

        rightCenter=
            rightVertex-R;

    }
    else {

        /*
           양면 오목렌즈

           왼쪽 면:
           중심이 왼쪽

           오른쪽 면:
           중심이 오른쪽
        */

        leftCenter=
            leftVertex-R;

        rightCenter=
            rightVertex+R;

    }


    return {

        left:{
            center:{
                x:leftCenter,
                y:axisY
            },
            R:R
        },

        right:{
            center:{
                x:rightCenter,
                y:axisY
            },
            R:R
        }

    };

}


/* =====================================================
   렌즈 그리기
===================================================== */

function drawLens(type) {

    const surfaces=
        lensSurfaces(type);

    const left=
        surfaces.left;

    const right=
        surfaces.right;


    const aperture=210;


    /*
       렌즈 외곽선
    */

    ctx.beginPath();


    /*
       왼쪽 표면
    */

    let leftStart=
        Math.asin(
            -aperture/left.R
        );

    let leftEnd=
        Math.asin(
            aperture/left.R
        );


    /*
       실제로는 중심각을 이용해
       위아래가 자연스럽게 연결되도록 그림
    */


    const steps=80;

    let first=true;


    for(
        let i=0;
        i<=steps;
        i++
    ) {

        const y=
            -aperture+
            (2*aperture*i/steps);


        const yy=
            y;


        const inside=
            Math.max(
                0,
                left.R*left.R-yy*yy
            );


        let sx;


        if(type==="convexLens") {

            sx=
                left.center.x-
                Math.sqrt(inside);

        }
        else {

            sx=
                left.center.x+
                Math.sqrt(inside);

        }


        const py=
            axisY+yy;


        if(first) {

            ctx.moveTo(sx,py);
            first=false;

        }
        else {

            ctx.lineTo(sx,py);

        }

    }


    /*
       오른쪽 표면을 아래에서 위로
    */

    for(
        let i=steps;
        i>=0;
        i--
    ) {

        const y=
            -aperture+
            (2*aperture*i/steps);


        const inside=
            Math.max(
                0,
                right.R*right.R-y*y
            );


        let sx;


        if(type==="convexLens") {

            sx=
                right.center.x+
                Math.sqrt(inside);

        }
        else {

            sx=
                right.center.x-
                Math.sqrt(inside);

        }


        const py=
            axisY+y;

        ctx.lineTo(sx,py);

    }


    ctx.closePath();


    ctx.fillStyle=
        "rgba(80,170,255,0.25)";

    ctx.fill();

    ctx.strokeStyle="#1976d2";
    ctx.lineWidth=4;

    ctx.stroke();


    text(
        type==="convexLens"
        ? "볼록렌즈"
        : "오목렌즈",
        objectX()-45,
        70,
        18
    );


    /*
       초점 표시

       얇은 렌즈 근사에서
       1/f = (n-1)(1/R1 - 1/R2)

       여기서는 실제 광선 추적과
       시각적 초점 표시를 위해
       곡률을 기준으로 표시
    */

    const n=
        parseFloat(material.value);

    const R=300;

    let f;

    if(type==="convexLens") {

        f=
            R/(2*(n-1));

    }
    else {

        f=
            -R/(2*(n-1));

    }


    /*
       화면 크기에 맞게 제한
    */

    const displayF=
        Math.max(
            80,
            Math.min(
                300,
                Math.abs(f)
            )
        );


    if(type==="convexLens") {

        drawFocus(
            objectX()+displayF,
            axisY,
            "F"
        );

        drawFocus(
            objectX()-displayF,
            axisY,
            "F"
        );

    }
    else {

        drawFocus(
            objectX()-displayF,
            axisY,
            "F"
        );

    }

}


/* =====================================================
   초점
===================================================== */

function drawFocus(x,y,label) {

    ctx.beginPath();

    ctx.arc(
        x,
        y,
        6,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#1976d2";

    ctx.fill();

    text(
        label,
        x+9,
        y-9,
        17,
        "#1976d2"
    );

}


/* =====================================================
   렌즈 광선 추적
===================================================== */

function traceLens(type) {

    const surfaces=
        lensSurfaces(type);

    const n=
        parseFloat(material.value);


    let p={
        x:laser.x,
        y:laser.y
    };


    let d={
        x:Math.cos(laser.angle),
        y:Math.sin(laser.angle)
    };


    /*
       첫 번째 표면
    */

    const first=
        rayCircleIntersection(
            p,
            d,
            surfaces.left.center,
            surfaces.left.R
        );


    if(!first) {

        line(
            p,
            add(p,mul(d,1000)),
            "#ff2020",
            4
        );

        return;

    }


    /*
       실제 렌즈 높이 범위
    */

    if(
        Math.abs(
            first.point.y-axisY
        )>210
    ) {

        line(
            p,
            add(p,mul(d,1000)),
            "#ff2020",
            4
        );

        return;

    }


    /*
       입사광
    */

    line(
        p,
        first.point,
        "#ff2020",
        4
    );


    /*
       첫 번째 면의 법선
    */

    let N1=
        norm(
            sub(
                first.point,
                surfaces.left.center
            )
        );


    /*
       공기 → 렌즈
    */

    let dInside=
        refract(
            d,
            N1,
            1.0,
            n
        );


    /*
       전반사가 일어나는 경우
    */

    if(!dInside) {

        const reflected=
            reflect(d,N1);

        line(
            first.point,
            add(
                first.point,
                mul(reflected,600)
            ),
            "#ff2020",
            4
        );

        return;

    }


    /*
       렌즈 내부에서 두 번째 면 찾기
    */

    const second=
        rayCircleIntersection(
            first.point,
            dInside,
            surfaces.right.center,
            surfaces.right.R
        );


    if(!second) {

        line(
            first.point,
            add(
                first.point,
                mul(dInside,600)
            ),
            "#ff2020",
            4
        );

        return;

    }


    /*
       렌즈 내부 광선
    */

    line(
        first.point,
        second.point,
        "#ff2020",
        4
    );


    /*
       두 번째 면 법선
    */

    let N2=
        norm(
            sub(
                second.point,
                surfaces.right.center
            )
        );


    /*
       렌즈 → 공기
    */

    let dOut=
        refract(
            dInside,
            N2,
            n,
            1.0
        );


    /*
       전반사
    */

    if(!dOut) {

        dOut=
            reflect(
                dInside,
                N2
            );

    }


    /*
       최종 굴절광
    */

    line(
        second.point,
        add(
            second.point,
            mul(dOut,700)
        ),
        "#ff2020",
        4
    );

}


/* =====================================================
   프리즘 꼭짓점
===================================================== */

function prismVertices() {

    const x=objectX();

    const angle=
        parseFloat(
            prismAngle.value
        )*
        Math.PI/180;


    const base=300;

    const height=
        base/
        (2*Math.tan(angle/2));


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


/* =====================================================
   프리즘 그리기
===================================================== */

function drawPrism() {

    const v=
        prismVertices();


    ctx.beginPath();

    ctx.moveTo(v[0].x,v[0].y);

    ctx.lineTo(v[1].x,v[1].y);

    ctx.lineTo(v[2].x,v[2].y);

    ctx.closePath();


    ctx.fillStyle=
        "rgba(80,170,255,0.25)";

    ctx.fill();

    ctx.strokeStyle="#1976d2";
    ctx.lineWidth=4;

    ctx.stroke();


    text(
        "프리즘",
        objectX()-25,
        v[2].y+40,
        18
    );

}


/* =====================================================
   프리즘 광선
===================================================== */

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
        x:Math.cos(laser.angle),
        y:Math.sin(laser.angle)
    };


    const edges=[

        [vertices[0],vertices[1]],

        [vertices[1],vertices[2]],

        [vertices[2],vertices[0]]

    ];


    /*
       첫 번째 면
    */

    let firstHit=null;
    let firstIndex=-1;


    for(
        let i=0;
        i<edges.length;
        i++
    ) {

        const hit=
            raySegmentIntersection(
                p,
                d,
                edges[i][0],
                edges[i][1]
            );


        if(
            hit &&
            (
                firstHit===null ||
                hit.t<firstHit.t
            )
        ) {

            firstHit=hit;
            firstIndex=i;

        }

    }


    /*
       프리즘에 닿지 않으면
       그냥 직진
    */

    if(!firstHit) {

        line(
            p,
            add(p,mul(d,1000)),
            "#ff2020",
            4
        );

        return;

    }


    /*
       첫 번째 면까지
    */

    line(
        p,
        firstHit.point,
        "#ff2020",
        4
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
        norm({
            x:-edge1.y,
            y:edge1.x
        });


    /*
       공기 → 유리
    */

    let dInside=
        refract(
            d,
            N1,
            1.0,
            n
        );


    /*
       전반사
    */

    if(!dInside) {

        dInside=
            reflect(
                d,
                N1
            );

        line(
            firstHit.point,
            add(
                firstHit.point,
                mul(dInside,600)
            ),
            "#ff2020",
            4
        );

        return;

    }


    /*
       두 번째 면 찾기

       첫 번째 면은 제외
    */

    let secondHit=null;
    let secondIndex=-1;


    for(
        let i=0;
        i<edges.length;
        i++
    ) {

        if(i===firstIndex) {
            continue;
        }


        const hit=
            raySegmentIntersection(
                firstHit.point,
                dInside,
                edges[i][0],
                edges[i][1]
            );


        if(
            hit &&
            (
                secondHit===null ||
                hit.t<secondHit.t
            )
        ) {

            secondHit=hit;
            secondIndex=i;

        }

    }


    /*
       프리즘 내부에서 두 번째 면까지
    */

    if(secondHit) {

        line(
            firstHit.point,
            secondHit.point,
            "#ff2020",
            4
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
            norm({
                x:-edge2.y,
                y:edge2.x
            });


        /*
           프리즘 → 공기
        */

        let dOut=
            refract(
                dInside,
                N2,
                n,
                1.0
            );


        /*
           전반사
        */

        if(!dOut) {

            dOut=
                reflect(
                    dInside,
                    N2
                );

        }


        /*
           최종 광선

           중요:
           여기에서만 최종 광선을 그린다.
           따라서 프리즘에서
           광선이 두 개 생기는 문제가 없다.
        */

        line(
            secondHit.point,
            add(
                secondHit.point,
                mul(dOut,700)
            ),
            "#ff2020",
            4
        );

    }
    else {

        /*
           프리즘 내부에서 계속 진행
        */

        line(
            firstHit.point,
            add(
                firstHit.point,
                mul(dInside,700)
            ),
            "#ff2020",
            4
        );

    }

}


/* =====================================================
   전체 그리기
===================================================== */

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

    if(type==="planeMirror") {

        drawPlaneMirror();

    }

    else if(
        type==="concaveMirror" ||
        type==="convexMirror"
    ) {

        drawCurvedMirror(type);

    }

    else if(
        type==="convexLens" ||
        type==="concaveLens"
    ) {

        drawLens(type);

    }

    else if(type==="prism") {

        drawPrism();

    }


    /*
       광선
    */

    if(type==="planeMirror") {

        tracePlaneMirror();

    }

    else if(
        type==="concaveMirror" ||
        type==="convexMirror"
    ) {

        traceCurvedMirror(type);

    }

    else if(
        type==="convexLens" ||
        type==="concaveLens"
    ) {

        traceLens(type);

    }

    else if(type==="prism") {

        tracePrism();

    }


    /*
       마지막에 레이저를 그린다.

       광선 자체는 위에서 한 번만 계산하므로
       프리즘에서 두 개가 나오는 문제가 없다.
    */

    drawLaser();


    /*
       정보 표시
    */

    const deg=
        laser.angle*180/Math.PI;

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


/* =====================================================
   물리 정보
===================================================== */

function updatePhysicsInfo() {

    const type=
        objectType.value;


    const n=
        parseFloat(material.value);


    let message="";


    if(
        type==="convexLens" ||
        type==="concaveLens"
    ) {

        message=
        "렌즈 재질의 굴절률 n = "
        +n.toFixed(2)
        +"이며, 중심 두께는 "
        +thickness.value
        +"입니다. "
        +"두께 변화는 굴절률 자체를 바꾸지 않고 "
        +"두 굴절면의 위치와 렌즈의 형상을 바꿉니다.";

    }

    else if(type==="planeMirror") {

        message=
        "평면거울에서는 입사각과 반사각이 같도록 "
        +"반사 법칙을 적용했습니다.";

    }

    else if(
        type==="concaveMirror" ||
        type==="convexMirror"
    ) {

        message=
        "곡면거울에서는 광선과 원형 곡면의 교점을 계산한 뒤 "
        +"그 지점의 법선을 구하고 반사의 법칙을 적용합니다. "
        +"곡률반지름 = "
        +radius.value;

    }

    else if(type==="prism") {

        message=
        "프리즘의 굴절률 n = "
        +parseFloat(prismIndex.value).toFixed(2)
        +"이며, 빛이 첫 번째 면과 두 번째 면에서 각각 "
        +"스넬의 법칙에 따라 굴절합니다.";

    }


    document.getElementById(
        "physicsInfo"
    ).textContent=
        message;

}


/* =====================================================
   마우스 좌표
===================================================== */

function mousePosition(event) {

    const rect=
        canvas.getBoundingClientRect();

    return {

        x:
        (event.clientX-rect.left)
        *W/rect.width,

        y:
        (event.clientY-rect.top)
        *H/rect.height

    };

}


/* =====================================================
   손잡이 드래그 시작
===================================================== */

canvas.addEventListener(
    "mousedown",
    function(event) {

        const p=
            mousePosition(event);

        const h=
            handlePosition();


        const distance=
            Math.sqrt(
                (p.x-h.x)*(p.x-h.x)+
                (p.y-h.y)*(p.y-h.y)
            );


        if(distance<35) {

            dragging=true;

            canvas.style.cursor=
                "grabbing";

        }

    }
);


/* =====================================================
   손잡이 드래그
===================================================== */

canvas.addEventListener(
    "mousemove",
    function(event) {

        const p=
            mousePosition(event);

        const h=
            handlePosition();


        if(!dragging) {

            const distance=
                Math.sqrt(
                    (p.x-h.x)*(p.x-h.x)+
                    (p.y-h.y)*(p.y-h.y)
                );


            if(distance<35) {

                canvas.style.cursor=
                    "grab";

            }
            else {

                canvas.style.cursor=
                    "default";

            }

            return;

        }


        /*
           레이저 중심에서
           마우스 방향으로 각도 계산
        */

        laser.angle=
            Math.atan2(
                p.y-laser.y,
                p.x-laser.x
            );


        draw();

    }
);


/* =====================================================
   드래그 종료
===================================================== */

window.addEventListener(
    "mouseup",
    function() {

        dragging=false;

        canvas.style.cursor=
            "default";

    }
);


/* =====================================================
   터치 화면 지원
===================================================== */

canvas.addEventListener(
    "touchstart",
    function(event) {

        const touch=
            event.touches[0];

        const rect=
            canvas.getBoundingClientRect();

        const p={

            x:
            (touch.clientX-rect.left)
            *W/rect.width,

            y:
            (touch.clientY-rect.top)
            *H/rect.height

        };


        const h=
            handlePosition();


        const distance=
            Math.sqrt(
                (p.x-h.x)*(p.x-h.x)+
                (p.y-h.y)*(p.y-h.y)
            );


        if(distance<45) {

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
            (touch.clientX-rect.left)
            *W/rect.width,

            y:
            (touch.clientY-rect.top)
            *H/rect.height

        };


        laser.angle=
            Math.atan2(
                p.y-laser.y,
                p.x-laser.x
            );


        draw();

    },
    {passive:false}
);


canvas.addEventListener(
    "touchend",
    function() {

        dragging=false;

    }
);


/* =====================================================
   컨트롤 변경
===================================================== */

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


/* =====================================================
   컨트롤 표시 업데이트
===================================================== */

function updateControls() {

    const type=
        objectType.value;


    /*
       렌즈
    */

    const isLens=
        type==="convexLens" ||
        type==="concaveLens";


    /*
       곡면거울
    */

    const isCurvedMirror=
        type==="concaveMirror" ||
        type==="convexMirror";


    /*
       프리즘
    */

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
        isCurvedMirror
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


/* =====================================================
   값 표시
===================================================== */

thickness.addEventListener(
    "input",
    function() {

        document.getElementById(
            "thicknessValue"
        ).textContent=
            thickness.value+" px";

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
            prismAngle.value+"°";

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

        const n=
            parseFloat(material.value);

        document.getElementById(
            "materialValue"
        ).textContent=
            "n = "+n.toFixed(2);

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


/* =====================================================
   초기 실행
===================================================== */

updateControls();

</script>

</body>
</html>
"""

components.html(
    html,
    height=1050,
    scrolling=False
)
