#version 460 core

#define PHI 1.61803398874989484820459

layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba8, location=0) uniform image2D tex;
layout(rgba8, location=1) uniform image2D out_tex;
layout(rgba8, location=2) uniform image2D static_tex;

// Taken from https://www.rastergrid.com/blog/2010/09/efficient-gaussian-blur-with-linear-sampling/

uniform float delta_time;
uniform int decay_rate;

void main(void) {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    vec4 sum = vec4(0.0);
    float weight_sum = 0;
    for (int x = -1; x < 2; x++) {
        for (int y = -1; y < 2; y++) {
            ivec2 pixel = ivec2(pos.x + x, pos.y + y);
            float weight = 2 - distance(pos, pixel);
            sum += imageLoad(tex, pixel) * weight;
            weight_sum += weight;
        }
    }

    vec4 colour = sum / weight_sum;
    vec4 new_col = colour - vec4(decay_rate * delta_time);
    imageStore(out_tex, pos, max(vec4(0), max(new_col, imageLoad(static_tex, pos))));
}
