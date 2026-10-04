#version 330 core

uniform sampler2D canvasTex;
uniform sampler2D noiseTex;
uniform float transitionTimer;
uniform int transitionState;
uniform float shakeTimer = -1.0;
uniform float caTimer = 0;
uniform float t;
uniform float killTimer = -1.0;
uniform float comboShowTimer = -1.0;
uniform vec2 offset;
in vec2 uvs;
out vec4 f_color;

const float PI = 3.14159265359;
const vec2 gridSize = vec2(64, 64);
const float caCoef = 0.005;
const float shakeCoef = 0.01;

const vec2 screenSize = vec2(640, 360);
const vec3 PURPLE_1 = vec3(75, 65, 88)/255;
const vec3 PURPLE_2 = vec3(53, 43, 66)/255;
const vec3 WHITE    = vec3(242, 240, 229)/255;
const vec3 RED_1    = vec3(105, 6, 33)/255;
const vec3 BLACK    = vec3(33, 33, 35)/255;

vec2 rotateVec(vec2 vec, float theta) {
    return vec.x * vec2(cos(theta), sin(theta))
    + vec.y * vec2(sin(theta), -cos(theta));
}

float linearEase(float x) {
    return -2*abs(x - 0.5) + 1;
}

float random2d(vec2 coord){
    return fract(sin(dot(coord.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    f_color = vec4(texture(canvasTex, uvs).rgb, 1.0);

    vec2 uvsS = vec2(uvs.x, uvs.y * screenSize.y/screenSize.x);
    vec2 uvsPx = vec2(floor(uvs*screenSize)/screenSize);
    vec2 uvsSPx = vec2(uvsPx.x, uvsPx.y * (screenSize.y/screenSize.x));
    vec2 uvsScreen = uvs*screenSize;

    float centerDist = distance(uvs, vec2(0.5, 0.5));

    // Blurry shake
    if (shakeTimer >= 0) {
        float shakeIntensity = (1 - shakeTimer)*centerDist * shakeCoef;
        vec2 shakeSampleVec = vec2(0.0, shakeIntensity);
        vec4 caSample1 = texture(canvasTex, uvs + shakeSampleVec);
        vec4 caSample2 = texture(canvasTex, uvs - rotateVec(shakeSampleVec, 2.0*PI/3.0));
        vec4 caSample3 = texture(canvasTex, uvs - rotateVec(shakeSampleVec, 4.0*PI/3.0));
        vec4 sampleMix = mix( mix(caSample1, caSample2, 0.5), caSample3, 0.5 );
        f_color = mix(f_color, sampleMix, 0.5);
    }

    // Chromatic abberation
    float caTimer2 = caTimer + 0.15;
    if (caTimer2 >= 0.0) {
        float caIntensity = caTimer2*centerDist * caCoef;
        vec2 sampleVec = vec2(0.0, caIntensity);
        float caSample1 = texture(canvasTex, uvs + sampleVec).r;
        float caSample2 = texture(canvasTex, uvs - rotateVec(sampleVec, 2.0*PI/3.0)).g;
        float caSample3 = texture(canvasTex, uvs - rotateVec(sampleVec, 4.0*PI/3.0)).b;
        f_color.r = caSample1;
        f_color.g = caSample2;
        f_color.b = caSample3;
    }

    if (length(f_color.rgb - PURPLE_1) < 0.001) {
        float n1 = texture(noiseTex, uvsSPx + vec2(0.31, 0.37) + 0.001*vec2(t)).r;
        float n2 = texture(noiseTex, uvsSPx - 0.001*vec2(t)).r;
        float n = clamp(n1+n2, 0, 1);

        float c = smoothstep(0.5, 1.0, uvsPx.y-offset.y/screenSize[1]);
        float k = smoothstep(0.3, 1.0, uvsPx.y-offset.y/screenSize[1]);

        float v = clamp(c+c*n, 0, 1);

        // f_color.rgb = mix(PURPLE_1, PURPLE_2, v);

        if (v > 0.1) {
            f_color.rgb = vec3(PURPLE_2);
            // f_color = mix(f_color, texture(canvasTex, vec2(uvs.x+offset.x, 1) + vec2(0 -uvs.y-offset)), 0.5);
        }
        else {
            f_color.rgb = vec3(PURPLE_1);
        }

    }

    if (length(f_color.rgb - vec3(0, 1, 1)) < 0.001) {
        float n = texture(noiseTex, 5*vec2(uvsS-offset/screenSize+0.0005*vec2(0, t))).r;
        f_color.rgb = vec3(0, 0.1+pow(n, 0.5), 1.2*n);
        // f_color.rgb = vec3(0, 1-n, 1.2*n);
    }


    if (uvsScreen.y > 65 && uvsScreen.y < 80) {

        if (length(f_color.rgb - WHITE) > 0.001) {

            float n = texture(noiseTex, 5*(uvsSPx+vec2(0.002*t, 0))).r;

            float k = pow(killTimer, 0.5) + 0.00001*comboShowTimer;

            float leftBound = mix(1, mix(0.4, 0.6, k), comboShowTimer);
            float rightBound = mix(1, 0.8, comboShowTimer);
            float nIntensity = smoothstep(leftBound, rightBound, uvsPx.x);

            float finalIntensity = nIntensity*n;

            if (finalIntensity > 0.2) {
                f_color.rgb = RED_1;
            }


            // f_color.r *= 1+intensity + nIntensity*n;
            // f_color.r *= 1+intensity + nIntensity*n;

        }

    }

    float vignette = 1*centerDist* mix(0.5, 1, random2d(uvs));
    vignette -= 0.4;
    f_color.r *= 1-vignette;
    f_color.g *= 1-0.9*vignette;
    f_color.b *= 1-0.8*vignette;
    f_color *= mix(0.9, 1, random2d(uvs));


    /*
    0  No transition
    1  Starting transition
    -1 Ending transition
    */
    if (transitionState != 0) { 
        float tTimer = transitionTimer;
        if (transitionState == 1) {
            tTimer = 1.0 - transitionTimer;
        }
        f_color.r *= clamp(tTimer, 0, 1);
        f_color.g *= clamp(1.2*tTimer, 0, 1);
        f_color.b *= clamp(1.5*tTimer, 0, 1);
        // f_color *= tTimer;
        // f_color.rb *= tTimer;

    }
}

