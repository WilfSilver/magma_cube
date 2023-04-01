#version 460 core

#define PHI 1.61803398874989484820459

layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba8, location=0) uniform image2D tex;

// Taken from https://www.rastergrid.com/blog/2010/09/efficient-gaussian-blur-with-linear-sampling/

uniform float offset[3] = float[](0.0, 1.3846153846, 3.2307692308);
uniform float weight[3] = float[](0.5, 0.5, 0.5);

void main(void) {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    vec4 color = vec4(0.0);
    for (int i=1; i<2; i++) {
        ivec2 ydelta = ivec2(pos + ivec2(0.0, offset[i]));
        color += imageLoad(tex, ivec2(ydelta))* weight[i];
        ivec2 xdelta = ivec2(pos - ivec2(offset[i], 0.0));
        color += imageLoad(tex, ivec2(xdelta))* weight[i];
        imageStore(tex, pos, color);
    }
}
