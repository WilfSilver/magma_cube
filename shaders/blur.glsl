#version 460 core

#define PHI 1.61803398874989484820459

layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba8, location=0) uniform image2D tex;
layout(rgba8, location=1) uniform image2D out_tex;

// Taken from https://www.rastergrid.com/blog/2010/09/efficient-gaussian-blur-with-linear-sampling/

uniform float offset[4] = float[](-2.0, -1.0, 1.0, 2.0);
uniform float weight[4] = float[](0.3, 0.3, 0.3, 0.3);
uniform float delta_time;
uniform int decay_rate;

void main(void) {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    // vec4 color = vec4(0.0);
    // for (int i=1; i<4; i++) {
    //     ivec2 ydelta = ivec2(pos + ivec2(0.0, offset[i]));
    //     color += imageLoad(tex, ydelta) * weight[i];
    //     ivec2 xdelta = ivec2(pos - ivec2(offset[i], 0));
    //     color += imageLoad(tex, ivec2(xdelta)) * weight[i];
    //     imageStore(out_tex, pos, color);
    // }
    vec4 new_col = imageLoad(tex, pos) - vec4(decay_rate * delta_time);
    imageStore(out_tex, pos, max(vec4(0), new_col));

}
