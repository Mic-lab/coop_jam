#version 330 core

uniform sampler2D canvasTex;
uniform sampler2D noiseTex;
uniform float transitionTimer;
uniform int transitionState;
uniform float shakeTimer = -1.0;
uniform float caTimer = -1.0;
uniform float t;
uniform float killTimer = -1.0;
uniform float comboShowTimer = -1.0;
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

vec2 rotateVec(vec2 vec, float theta) {
    return vec.x * vec2(cos(theta), sin(theta))
    + vec.y * vec2(sin(theta), -cos(theta));
}

float linearEase(float x) {
    return -2*abs(x - 0.5) + 1;
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
    if (caTimer >= 0.0) {
        float caIntensity = caTimer*centerDist * caCoef;
        vec2 sampleVec = vec2(0.0, caIntensity);
        float caSample1 = texture(canvasTex, uvs + sampleVec).r;
        float caSample2 = texture(canvasTex, uvs - rotateVec(sampleVec, 2.0*PI/3.0)).g;
        float caSample3 = texture(canvasTex, uvs - rotateVec(sampleVec, 4.0*PI/3.0)).b;
        f_color.r = caSample1;
        f_color.g = caSample2;
        f_color.b = caSample3;
    }

    if (f_color.rgb == vec3(0)) {
        float n1 = texture(noiseTex, uvsSPx + vec2(0.31, 0.37) + 0.001*vec2(t)).r;
        float n2 = texture(noiseTex, uvsSPx - 0.001*vec2(t)).r;
        float n = clamp(n1+n2, 0, 1);

        float c = smoothstep(0.8, 1.0, uvsPx.y);
        float k = smoothstep(0.3, 1.0, uvsPx.y);

        float v = clamp(c+c*n, 0, 1);

        f_color.rgb = mix(PURPLE_1, PURPLE_2, v);

        // if (v > 0.5) {
        //     f_color.rgb = vec3(PURPLE_2);
        // }
        // else {
        //     f_color.rgb = vec3(PURPLE_1);
        // }
    }

    if (uvsScreen.y > 40 && uvsScreen.y < 55) {

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
        f_color.g *= clamp(1.5*tTimer, 0, 1);
        f_color.b *= clamp(2*tTimer, 0, 1);
        // f_color *= tTimer;
        // f_color.rb *= tTimer;

    }
}

