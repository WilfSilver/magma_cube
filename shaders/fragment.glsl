#version 460

uniform sampler2D RTScene;
varying vec2 vTexCoord;

uniform float ww;
uniform float wh; 

const float xBlursize = 1.0/ww;
const float yBlursize = 1.0/wh;

void main(void)
{
    vec4 sumXBLur = vec4(0.0);
    vec4 sumYBLur = vec4(0.0);

    // blur in y (vertical)
    // take nine samples, with the distance xBlursize between them
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x - 4.0*xBlursize, vTexCoord.y)) * 0.05;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x - 3.0*xBlursize, vTexCoord.y)) * 0.09;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x - 2.0*xBlursize, vTexCoord.y)) * 0.12;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x - xBlursize, vTexCoord.y)) * 0.15;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x, vTexCoord.y)) * 0.16;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x + xBlursize, vTexCoord.y)) * 0.15;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x + 2.0*xBlursize, vTexCoord.y)) * 0.12;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x + 3.0*xBlursize, vTexCoord.y)) * 0.09;
    sumXBLur += texture2D(RTScene, vec2(vTexCoord.x + 4.0*xBlursize, vTexCoord.y)) * 0.05;

    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y - 4.0*yBlursize)) * 0.05;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y - 3.0*yBlursize)) * 0.09;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y - 2.0*yBlursize)) * 0.12;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y - yBlursize)) * 0.15;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y)) * 0.16;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y + yBlursize)) * 0.15;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y + 2.0*yBlursize)) * 0.12;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y + 3.0*yBlursize)) * 0.09;
    sumYBLur += texture2D(RTBlurH, vec2(vTexCoord.x, vTexCoord.y + 4.0*xBlursize)) * 0.05;

    gl_FragColor = (sumXBLur + sumYBlur)/2;

}   