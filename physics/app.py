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
    **렌즈·거울·프리즘에 레이저를 직접 쏘아 빛의 반사와 굴절을 관찰하는 시뮬레이터입니다.**

    왼쪽의 레이저 손잡이를 마우스로 드래그하면 레이저의 방향이 바뀝니다.
    """
)

html_code = r"""
<!DOCTYPE html>
<html>
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
}

#main {
    width: 100%;
}

#toolbar {
    background: white;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.row {
    display: flex;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
}

label {
    font-weight: bold;
}

select {
    padding: 7px 10px;
    border-radius: 6px;
    border: 1px solid #aaa;
    font-size: 15px;
}

input[type="range"] {
    width: 180px;
}

#angleText,
#refractiveText {
    font-weight: bold;
}

#canvasBox {
    position: relative;
    width: 100%;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

canvas {
    display: block;
    width: 100%;
    height: auto;
    cursor: default;
}

#info {
    background: white;
    margin-top: 12px;
    padding: 15px;
    border-radius: 12px;
    line-height: 1.7;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.info-title {
    font-weight: bold;
    font-size: 17px;
}

.highlight {
    font-weight: bold;
}

#help {
    margin-top: 10px;
    color: #555;
    font-size: 14px;
}

</style>

</head>

<body>

<div id="main">

    <div id="toolbar">

        <div class="row">

            <label>광학 기구</label>

            <select id="objectType">

                <option value="convexLens">볼록렌즈</option>
                <option value="concaveLens">오목렌즈</option>

                <option value="planeMirror">평면거울</option>
                <option value="convexMirror">볼록거울</option>
                <option value="concaveMirror">오목거울</option>

                <option value="prism">프리즘</option>

            </select>

            <label>굴절률</label>

            <input
                id="refractive"
                type="range"
                min="1.1"
                max="2.0"
                step="0.01"
                value="1.50"
            >

            <span id="refractiveText">1.50</span>

        </div>

        <div id="help">
            🟡 레이저 광원의 손잡이를 마우스로 드래그하여 레이저의 방향을 바꿔보세요.
        </div>

    </div>


    <div id="canvasBox">

        <canvas id="canvas" width="1100" height="650"></canvas>

    </div>


    <div id="info">

        <div class="info-title">실험 정보</div>

        <div>
            선택한 광학 기구:
            <span id="objectText" class="highlight">볼록렌즈</span>
        </div>

        <div>
            레이저 각도:
            <span id="angleText" class="highlight">0°</span>
        </div>

        <div>
            굴절률:
            <span id="refractiveInfo" class="highlight">1.50</span>
        </div>

        <div id="explanation"></div>

    </div>

</div>


<script>

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const objectSelect = document.getElementById("objectType");
const refractiveSlider = document.getElementById("refractive");

const angleText = document.getElementById("angleText");
const objectText = document.getElementById("objectText");
const refractiveText = document.getElementById("refractiveText");
const refractiveInfo = document.getElementById("refractiveInfo");
const explanation = document.getElementById("explanation");


/* -------------------------------------------------------
   기본 설정
------------------------------------------------------- */

const W = canvas.width;
const H = canvas.height;

const opticalX = 650;
const opticalY = 325;

const laserX = 120;
const laserY = 325;

let laserAngle = 0;

let draggingHandle = false;


/* -------------------------------------------------------
   벡터 함수
------------------------------------------------------- */

function add(a,b) {
    return {
        x: a.x + b.x,
        y: a.y + b.y
    };
}

function sub(a,b) {
    return {
        x: a.x - b.x,
        y: a.y - b.y
    };
}

function mul(a,k) {
    return {
        x: a.x * k,
        y: a.y * k
    };
}

function dot(a,b) {
    return a.x*b.x + a.y*b.y;
}

function length(v) {
    return Math.sqrt(v.x*v.x + v.y*v.y);
}

function normalize(v) {

    const l = length(v);

    if (l === 0) {
        return {x:1,y:0};
    }

    return {
        x:v.x/l,
        y:v.y/l
    };
}


/* -------------------------------------------------------
   선 그리기
------------------------------------------------------- */

function drawLine(p1,p2,color,width=3,dash=false) {

    ctx.beginPath();

    if (dash) {
        ctx.setLineDash([8,7]);
    } else {
        ctx.setLineDash([]);
    }

    ctx.moveTo(p1.x,p1.y);
    ctx.lineTo(p2.x,p2.y);

    ctx.strokeStyle=color;
    ctx.lineWidth=width;

    ctx.stroke();

    ctx.setLineDash([]);
}


/* -------------------------------------------------------
   텍스트
------------------------------------------------------- */

function drawText(text,x,y,size=15,color="#222") {

    ctx.fillStyle=color;
    ctx.font=size+"px Arial";
    ctx.fillText(text,x,y);

}


/* -------------------------------------------------------
   광축
------------------------------------------------------- */

function drawAxis() {

    drawLine(
        {x:40,y:opticalY},
        {x:1060,y:opticalY},
        "#999",
        1,
        true
    );

    drawText(
        "광축",
        1010,
        opticalY-10,
        13,
        "#777"
    );
}


/* -------------------------------------------------------
   레이저 광원
------------------------------------------------------- */

function drawLaser() {

    const dir = {
        x:Math.cos(laserAngle),
        y:Math.sin(laserAngle)
    };

    const handleLength = 70;

    const handleEnd = add(
        {x:laserX,y:laserY},
        mul(dir,handleLength)
    );


    /* 레이저 본체 */

    ctx.beginPath();

    ctx.arc(
        laserX,
        laserY,
        22,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#333";
    ctx.fill();

    ctx.strokeStyle="#111";
    ctx.lineWidth=3;
    ctx.stroke();


    /* 손잡이 */

    drawLine(
        {x:laserX,y:laserY},
        handleEnd,
        "#f5b400",
        12
    );


    /* 손잡이 끝 */

    ctx.beginPath();

    ctx.arc(
        handleEnd.x,
        handleEnd.y,
        13,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#ffd84d";
    ctx.fill();

    ctx.strokeStyle="#8a6500";
    ctx.lineWidth=2;

    ctx.stroke();


    /* 레이저 */

    const beamEnd = add(
        {x:laserX,y:laserY},
        mul(dir,250)
    );

    drawLine(
        {x:laserX,y:laserY},
        beamEnd,
        "#ff2020",
        4
    );


    /* 레이저 점 */

    ctx.beginPath();

    ctx.arc(
        laserX,
        laserY,
        7,
        0,
        Math.PI*2
    );

    ctx.fillStyle="#ff0000";
    ctx.fill();


    /* 방향 화살표 */

    const arrowStart = add(
        {x:laserX,y:laserY},
        mul(dir,45)
    );

    const arrowEnd = add(
        {x:laserX,y:laserY},
        mul(dir,85)
    );

    drawLine(
        arrowStart,
        arrowEnd,
        "#ff2020",
        3
    );


    drawText(
        "레이저 손잡이",
        laserX-45,
        laserY+55,
        14,
        "#555"
    );
}


/* -------------------------------------------------------
   평면 거울
------------------------------------------------------- */

function drawPlaneMirror() {

    const x=opticalX;

    drawLine(
        {x:x,y:120},
        {x:x,y:530},
        "#333",
        8
    );

    /* 거울 뒤쪽 무늬 */

    for(let y=130;y<530;y+=25) {

        drawLine(
            {x:x+5,y:y},
            {x:x+22,y:y+15},
            "#888",
            2
        );

    }

    drawText(
        "평면거울",
        x-35,
        100,
        18,
        "#222"
    );

}


/* -------------------------------------------------------
   곡면 거울
------------------------------------------------------- */

function drawCurvedMirror(type) {

    const cx=opticalX;
    const cy=opticalY;

    ctx.beginPath();

    if(type==="concaveMirror") {

        ctx.arc(
            cx+160,
            cy,
            160,
            Math.PI*0.72,
            Math.PI*1.28
        );

    } else {

        ctx.arc(
            cx-160,
            cy,
            160,
            -Math.PI*0.28,
            Math.PI*0.28
        );

    }

    ctx.strokeStyle="#333";
    ctx.lineWidth=8;
    ctx.stroke();


    drawText(
        type==="concaveMirror" ? "오목거울" : "볼록거울",
        cx-45,
        100,
        18,
        "#222"
    );

}


/* -------------------------------------------------------
   렌즈
------------------------------------------------------- */

function drawLens(type) {

    const x=opticalX;
    const cy=opticalY;

    ctx.beginPath();

    if(type==="convexLens") {

        ctx.moveTo(x,cy-160);

        ctx.bezierCurveTo(
            x-45,cy-100,
            x-45,cy+100,
            x,cy+160
        );

        ctx.bezierCurveTo(
            x+45,cy+100,
            x+45,cy-100,
            x,cy-160
        );

    } else {

        ctx.moveTo(x,cy-160);

        ctx.bezierCurveTo(
            x+45,cy-100,
            x+45,cy+100,
            x,cy+160
        );

        ctx.bezierCurveTo(
            x-45,cy+100,
            x-45,cy-100,
            x,cy-160
        );

    }

    ctx.closePath();

    ctx.fillStyle="rgba(100,180,255,0.25)";
    ctx.fill();

    ctx.strokeStyle="#1976d2";
    ctx.lineWidth=4;
    ctx.stroke();


    drawText(
        type==="convexLens" ? "볼록렌즈" : "오목렌즈",
        x-45,
        100,
        18,
        "#222"
    );


    /* 초점 표시 */

    const focalLength=130;

    if(type==="convexLens") {

        ctx.beginPath();

        ctx.arc(
            x+focalLength,
            cy,
            6,
            0,
            Math.PI*2
        );

        ctx.fillStyle="#1976d2";
        ctx.fill();

        drawText(
            "F",
            x+focalLength+10,
            cy-10,
            17,
            "#1976d2"
        );

        ctx.beginPath();

        ctx.arc(
            x-focalLength,
            cy,
            6,
            0,
            Math.PI*2
        );

        ctx.fillStyle="#1976d2";
        ctx.fill();

        drawText(
            "F",
            x-focalLength-20,
            cy-10,
            17,
            "#1976d2"
        );

    } else {

        ctx.beginPath();

        ctx.arc(
            x-focalLength,
            cy,
            6,
            0,
            Math.PI*2
        );

        ctx.fillStyle="#1976d2";
        ctx.fill();

        drawText(
            "F",
            x-focalLength-20,
            cy-10,
            17,
            "#1976d2"
        );

    }

}


/* -------------------------------------------------------
   프리즘
------------------------------------------------------- */

function drawPrism() {

    const x=opticalX;
    const cy=opticalY;

    ctx.beginPath();

    ctx.moveTo(
        x-100,
        cy+150
    );

    ctx.lineTo(
        x,
        cy-150
    );

    ctx.lineTo(
        x+150,
        cy+150
    );

    ctx.closePath();

    ctx.fillStyle="rgba(120,180,255,0.28)";
    ctx.fill();

    ctx.strokeStyle="#1976d2";
    ctx.lineWidth=4;
    ctx.stroke();


    drawText(
        "프리즘",
        x+10,
        cy+190,
        18,
        "#222"
    );

}


/* -------------------------------------------------------
   굴절 계산
------------------------------------------------------- */

function refract(I,N,n1,n2) {

    I=normalize(I);
    N=normalize(N);

    let cosi=Math.max(
        -1,
        Math.min(1,dot(I,N))
    );

    let etai=n1;
    let etat=n2;

    let normal={x:N.x,y:N.y};

    if(cosi<0) {

        cosi=-cosi;

    } else {

        const temp=etai;
        etai=etat;
        etat=temp;

        normal=mul(N,-1);

    }

    const eta=etai/etat;

    const k=1-eta*eta*(1-cosi*cosi);

    if(k<0) {

        return null;

    }

    return add(
        mul(I,eta),
        mul(
            normal,
            eta*cosi-Math.sqrt(k)
        )
    );

}


/* -------------------------------------------------------
   반사 계산
------------------------------------------------------- */

function reflect(I,N) {

    I=normalize(I);
    N=normalize(N);

    return sub(
        I,
        mul(
            N,
            2*dot(I,N)
        )
    );

}


/* -------------------------------------------------------
   간단한 렌즈 광선
------------------------------------------------------- */

function drawLensRays(type) {

    const dir={
        x:Math.cos(laserAngle),
        y:Math.sin(laserAngle)
    };

    const start={
        x:laserX,
        y:laserY
    };

    const lensX=opticalX;

    if(Math.abs(dir.x)<0.001) return;


    const distance=(lensX-start.x)/dir.x;

    const hitY=start.y+distance*dir.y;


    if(hitY<150 || hitY>500) {

        return;

    }


    const hit={
        x:lensX,
        y:hitY
    };


    drawLine(
        start,
        hit,
        "#ff2020",
        4
    );


    const focal=130;

    let target;

    if(type==="convexLens") {

        target={
            x:lensX+focal,
            y:opticalY
        };

    } else {

        target={
            x:lensX-focal,
            y:opticalY
        };

    }


    let outgoing;

    if(type==="convexLens") {

        outgoing=normalize(
            sub(target,hit)
        );

    } else {

        outgoing=normalize(
            sub(hit,target)
        );

    }


    const end=add(
        hit,
        mul(outgoing,500)
    );


    drawLine(
        hit,
        end,
        "#ff2020",
        4
    );


    if(type==="concaveLens") {

        drawLine(
            hit,
            target,
            "#ff7777",
            2,
            true
        );

    }

}


/* -------------------------------------------------------
   평면 거울 광선
------------------------------------------------------- */

function drawPlaneMirrorRay() {

    const dir={
        x:Math.cos(laserAngle),
        y:Math.sin(laserAngle)
    };

    const start={
        x:laserX,
        y:laserY
    };

    const mirrorX=opticalX;

    if(dir.x<=0) {

        drawLine(
            start,
            add(start,mul(dir,600)),
            "#ff2020",
            4
        );

        return;

    }

    const t=(mirrorX-start.x)/dir.x;

    const hit=add(
        start,
        mul(dir,t)
    );


    if(hit.y<100 || hit.y>550) {

        drawLine(
            start,
            add(start,mul(dir,600)),
            "#ff2020",
            4
        );

        return;

    }


    drawLine(
        start,
        hit,
        "#ff2020",
        4
    );


    const normal={
        x:-1,
        y:0
    };

    const reflected=reflect(dir,normal);

    drawLine(
        hit,
        add(hit,mul(reflected,500)),
        "#ff2020",
        4
    );

}


/* -------------------------------------------------------
   곡면 거울의 간단한 반사 표현
------------------------------------------------------- */

function drawCurvedMirrorRay(type) {

    const dir={
        x:Math.cos(laserAngle),
        y:Math.sin(laserAngle)
    };

    const start={
        x:laserX,
        y:laserY
    };


    const mirrorX=opticalX;

    if(dir.x<=0) {

        drawLine(
            start,
            add(start,mul(dir,600)),
            "#ff2020",
            4
        );

        return;

    }


    const t=(mirrorX-start.x)/dir.x;

    const hit=add(
        start,
        mul(dir,t)
    );


    if(hit.y<120 || hit.y>530) {

        drawLine(
            start,
            add(start,mul(dir,600)),
            "#ff2020",
            4
        );

        return;

    }


    drawLine(
        start,
        hit,
        "#ff2020",
        4
    );


    let reflected;


    if(type==="concaveMirror") {

        const focus={
            x:mirrorX-130,
            y:opticalY
        };

        reflected=normalize(
            sub(focus,hit)
        );

    } else {

        const virtualFocus={
            x:mirrorX+130,
            y:opticalY
        };

        reflected=normalize(
            sub(hit,virtualFocus)
        );

    }


    drawLine(
        hit,
        add(hit,mul(reflected,450)),
        "#ff2020",
        4
    );


    if(type==="convexMirror") {

        const virtualFocus={
            x:mirrorX+130,
            y:opticalY
        };

        drawLine(
            hit,
            virtualFocus,
            "#ff8888",
            2,
            true
        );

    }

}


/* -------------------------------------------------------
   프리즘 광선
------------------------------------------------------- */

function drawPrismRay() {

    const dir={
        x:Math.cos(laserAngle),
        y:Math.sin(laserAngle)
    };

    const start={
        x:laserX,
        y:laserY
    };


    /* 프리즘 위치 */

    const p1={
        x:opticalX-100,
        y:opticalY+150
    };

    const p2={
        x:opticalX,
        y:opticalY-150
    };

    const p3={
        x:opticalX+150,
        y:opticalY+150
    };


    /*
       단순화된 프리즘 광선.

       첫 번째 굴절
       → 프리즘 내부 진행
       → 두 번째 굴절
    */


    const first={
        x:opticalX-45,
        y:opticalY
    };


    drawLine(
        start,
        first,
        "#ff2020",
        4
    );


    const n1=1.0;

    const n2=parseFloat(
        refractiveSlider.value
    );


    let internalDir=refract(
        dir,
        {x:-0.8,y:-0.6},
        n1,
        n2
    );


    if(!internalDir) {

        internalDir=dir;

    }


    const second=add(
        first,
        mul(internalDir,250)
    );


    drawLine(
        first,
        second,
        "#ff2020",
        4
    );


    const finalDir=refract(
        internalDir,
        {x:0.89,y:0.45},
        n2,
        n1
    );


    let outDir=finalDir;

    if(!outDir) {

        outDir=internalDir;

    }


    drawLine(
        second,
        add(second,mul(outDir,450)),
        "#ff2020",
        4
    );

}


/* -------------------------------------------------------
   설명
------------------------------------------------------- */

function updateExplanation(type) {

    const explanations={

        convexLens:
        "볼록렌즈에서는 평행한 광선이 렌즈를 통과한 뒤 한 점인 초점 쪽으로 모이는 모습을 확인할 수 있습니다.",

        concaveLens:
        "오목렌즈에서는 광선이 바깥쪽으로 퍼지며, 뒤쪽으로 연장하면 가상 초점에서 나온 것처럼 보입니다.",

        planeMirror:
        "평면거울에서는 입사각과 반사각이 같아지는 반사의 법칙을 확인할 수 있습니다.",

        concaveMirror:
        "오목거울에서는 반사된 광선이 중심축 쪽으로 모이는 현상을 확인할 수 있습니다.",

        convexMirror:
        "볼록거울에서는 반사된 광선이 퍼지며 뒤쪽의 가상 초점에서 나온 것처럼 보입니다.",

        prism:
        "프리즘에서는 빛이 공기에서 프리즘으로 들어갈 때와 다시 공기로 나올 때 각각 굴절하는 모습을 확인할 수 있습니다."

    };

    explanation.innerHTML=
        explanations[type];

}


/* -------------------------------------------------------
   전체 화면 다시 그리기
------------------------------------------------------- */

function draw() {

    ctx.clearRect(
        0,
        0,
        W,
        H
    );


    /* 배경 */

    ctx.fillStyle="#ffffff";

    ctx.fillRect(
        0,
        0,
        W,
        H
    );


    drawAxis();


    const type=objectSelect.value;


    if(type==="convexLens") {

        drawLens("convexLens");
        drawLensRays("convexLens");

    }

    else if(type==="concaveLens") {

        drawLens("concaveLens");
        drawLensRays("concaveLens");

    }

    else if(type==="planeMirror") {

        drawPlaneMirror();
        drawPlaneMirrorRay();

    }

    else if(type==="concaveMirror") {

        drawCurvedMirror("concaveMirror");
        drawCurvedMirrorRay("concaveMirror");

    }

    else if(type==="convexMirror") {

        drawCurvedMirror("convexMirror");
        drawCurvedMirrorRay("convexMirror");

    }

    else if(type==="prism") {

        drawPrism();
        drawPrismRay();

    }


    drawLaser();


    /* 정보 */

    const degrees=
        laserAngle*180/Math.PI;

    angleText.textContent=
        degrees.toFixed(1)+"°";

    objectText.textContent=
        objectSelect.options[
            objectSelect.selectedIndex
        ].text;

    const n=
        parseFloat(refractiveSlider.value);

    refractiveText.textContent=
        n.toFixed(2);

    refractiveInfo.textContent=
        n.toFixed(2);

    updateExplanation(type);

}


/* -------------------------------------------------------
   마우스 좌표
------------------------------------------------------- */

function getMousePosition(event) {

    const rect=
        canvas.getBoundingClientRect();

    return {

        x:
        (event.clientX-rect.left)
        *canvas.width/rect.width,

        y:
        (event.clientY-rect.top)
        *canvas.height/rect.height

    };

}


/* -------------------------------------------------------
   손잡이 위치
------------------------------------------------------- */

function getHandlePosition() {

    return {

        x:
        laserX+
        Math.cos(laserAngle)*70,

        y:
        laserY+
        Math.sin(laserAngle)*70

    };

}


/* -------------------------------------------------------
   마우스 누르기
------------------------------------------------------- */

canvas.addEventListener(
    "mousedown",
    function(event) {

        const p=
            getMousePosition(event);

        const h=
            getHandlePosition();

        const distance=
            Math.sqrt(
                (p.x-h.x)*(p.x-h.x)+
                (p.y-h.y)*(p.y-h.y)
            );


        if(distance<30) {

            draggingHandle=true;

            canvas.style.cursor="grabbing";

        }

    }
);


/* -------------------------------------------------------
   마우스 움직이기
------------------------------------------------------- */

canvas.addEventListener(
    "mousemove",
    function(event) {

        const p=
            getMousePosition(event);

        const h=
            getHandlePosition();

        const distance=
            Math.sqrt(
                (p.x-h.x)*(p.x-h.x)+
                (p.y-h.y)*(p.y-h.y)
            );


        if(!draggingHandle) {

            if(distance<30) {

                canvas.style.cursor="grab";

            } else {

                canvas.style.cursor="default";

            }

            return;

        }


        laserAngle=
            Math.atan2(
                p.y-laserY,
                p.x-laserX
            );


        draw();

    }
);


/* -------------------------------------------------------
   마우스 놓기
------------------------------------------------------- */

window.addEventListener(
    "mouseup",
    function() {

        draggingHandle=false;

        canvas.style.cursor="default";

    }
);


/* -------------------------------------------------------
   터치 화면 지원
------------------------------------------------------- */

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
            *canvas.width/rect.width,

            y:
            (touch.clientY-rect.top)
            *canvas.height/rect.height

        };


        const h=
            getHandlePosition();


        const distance=
            Math.sqrt(
                (p.x-h.x)*(p.x-h.x)+
                (p.y-h.y)*(p.y-h.y)
            );


        if(distance<40) {

            draggingHandle=true;

        }

    }
);


canvas.addEventListener(
    "touchmove",
    function(event) {

        if(!draggingHandle) return;

        event.preventDefault();

        const touch=
            event.touches[0];

        const rect=
            canvas.getBoundingClientRect();

        const p={

            x:
            (touch.clientX-rect.left)
            *canvas.width/rect.width,

            y:
            (touch.clientY-rect.top)
            *canvas.height/rect.height

        };


        laserAngle=
            Math.atan2(
                p.y-laserY,
                p.x-laserX
            );


        draw();

    },
    {passive:false}
);


canvas.addEventListener(
    "touchend",
    function() {

        draggingHandle=false;

    }
);


/* -------------------------------------------------------
   선택 변경
------------------------------------------------------- */

objectSelect.addEventListener(
    "change",
    draw
);


refractiveSlider.addEventListener(
    "input",
    draw
);


/* 처음 실행 */

draw();

</script>

</body>
</html>
"""


components.html(
    html_code,
    height=900,
    scrolling=False
)
