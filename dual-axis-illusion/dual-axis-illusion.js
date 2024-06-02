"use strict";

const x = c.getContext('2d');
const PI = Math.PI;
const S = Math.sin;
const xCenter = c.width/2;
const yCenter = c.height/2;
const width = 450;
const height = 300;

let t = 0;

function DrawCurvePoint(pos, color, radius=30, stroke=0)
{
    let X = width*Math.sin(pos/3);
    let Y = height*Math.sin(t+pos/2);
    x.beginPath();
    x.arc(xCenter+X, yCenter+Y*.9, radius, 0, 7);
    x.fillStyle = color;
    x.strokeStyle = color;
    stroke ? x.stroke() : x.fill();
}

function Update()
{
    if (self !== top && !document.hasFocus())
        return;

    // get settings
    let spinAxis = document.querySelector('input[name="radio_spinAxis"]:checked').value;
    let spinDirection = parseFloat(document.querySelector('input[name="radio_spinDirection"]:checked').value);
    let showDots = checkbox_circleOverlaps.checked;

    // clear canvas
    c.width += 0;
    x.lineWidth = 10;
    t += spinDirection/60;   

    // draw curve
    let I = 1e3;
    for(let i=I; i--;)
        DrawCurvePoint(2*6*PI*i/I, "#000");

    if (!showDots)
    {
        if (spinAxis == 'horizontal')
        {
            // draw fade
            x.fillStyle = '#F00';
            for(let i=-32; i<=32; ++i)
            {
                x.globalAlpha = 2-2*Math.abs(i)/32;
                x.fillRect(0, yCenter+i*8, 2e3, 8);
            }
            x.globalAlpha = 1;

            // draw the front part of the curve again
            for(let i=I;i--;)
            {
                if (Math.sin(6*PI*i/I+2*PI+1.4+t) > 0)
                    DrawCurvePoint(2*6*PI*i/I, "#000");
            }
        }
        else if (spinAxis == 'vertical')
        {
            // draw fade
            x.fillStyle = '#08F';
            for(let i=-32; i<=32; ++i)
            {
                x.globalAlpha = 2-2*Math.abs(i)/32;
                x.fillRect(xCenter+i*12, 0, 12, 2e3);
            }
            x.globalAlpha = 1;
            
            // draw the front part of the curve again
            for(let i=I;i--;)
            {
                if (Math.sin(4*PI*i/I+2*PI/4) < 0)
                    DrawCurvePoint(2*6*PI*i/I, "#000");
            }
        }
    }
    else
    {
        if (spinAxis == 'horizontal' || spinAxis == '')
        {
            // draw dots on overlaps
            let color = '#F00';
            DrawCurvePoint( 1.57, color, 70, 1);
            DrawCurvePoint( 7.87, color, 70, 1);
            DrawCurvePoint(11.00, color, 70, 1);
            DrawCurvePoint(17.28, color, 70, 1);
        }
        if (spinAxis == 'vertical' || spinAxis == '')
        {
            // draw dots on overlaps
            // this part is a bit hacky, it should use DrawCurvePoint
            x.strokeStyle = '#08F';
            x.beginPath(), x.arc(xCenter+width*Math.sin(1.05+t*2/3), yCenter, 70, 0, 7), x.stroke();
            x.beginPath(), x.arc(xCenter+width*Math.sin(3.14+t*2/3), yCenter, 70, 0, 7), x.stroke();
            x.beginPath(), x.arc(xCenter+width*Math.sin(5.24+t*2/3), yCenter, 70, 0, 7), x.stroke();
        }
    }
}

setInterval(Update, 16);
